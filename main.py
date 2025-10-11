import httpx
import asyncio
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
import re
from collections import defaultdict
from urllib.parse import urlparse, urljoin

# [Keep all your EQUIPMENT_TYPES_PHRASES, ALL_BRANDS, PLASTIC_MATERIALS, METAL_MATERIALS, ALL_KEYWORDS from before]

EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,})\b', re.IGNORECASE)

def normalize_domain(domain):
    """Normalize domain for comparison"""
    return domain.lower().replace('www.', '')

def extract_domain_from_html(html):
    """Extract domain from HTML meta tags"""
    patterns = [
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']https?://([^/\?"\']+)',
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']https?://([^/\?"\']+)',
        r'<base[^>]+href=["\']https?://([^/\?"\']+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return normalize_domain(match.group(1))
    return None

def extract_internal_links(html, base_domain):
    """Extract all internal links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Skip anchors, javascript, mailto, tel
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        
        # Convert relative to absolute
        if href.startswith('/'):
            url = f'https://{base_domain}{href}'
        elif href.startswith('http'):
            url = href
        else:
            continue
        
        # Parse URL
        try:
            parsed = urlparse(url)
            link_domain = normalize_domain(parsed.netloc)
            
            # Only keep internal links
            if link_domain == normalize_domain(base_domain):
                # Remove fragments and query params
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                links.append(clean_url)
        except:
            continue
    
    # Dedupe and remove homepage variations
    unique_links = list(set(links))
    unique_links = [l for l in unique_links if not l.endswith('/') or len(urlparse(l).path) > 1]
    
    return unique_links

def is_valid_email(email):
    """Validate email"""
    if email.count('@') != 1:
        return False
    
    invalid_patterns = [
        '.png', '.jpg', '.css', '.js', 'example.com', 'noreply'
    ]
    
    return not any(p in email.lower() for p in invalid_patterns)

def detect_manufacturing_indicators(html, url):
    """Detect equipment, brands, materials"""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text().lower()
    combined = text + ' ' + url.lower()
    
    found = {
        'equipment_types': set(),
        'brands': set(),
        'keywords': set(),
        'materials': {'plastics': set(), 'metals': set()}
    }
    
    # Simplified - add your full lists here
    equipment_phrases = ['cnc machining', 'laser cutting', 'injection molding', 'extrusion']
    brands = ['haas', 'mazak', 'engel', 'arburg', 'trumpf']
    keywords = ['cnc', 'laser', 'welding', 'molding']
    plastics = ['abs', 'nylon', 'polycarbonate', 'pet']
    metals = ['aluminum', 'stainless steel', '6061', 'titanium']
    
    for phrase in equipment_phrases:
        if phrase in combined:
            found['equipment_types'].add(phrase)
    
    for brand in brands:
        if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    for kw in keywords:
        if kw in combined:
            found['keywords'].add(kw)
    
    for p in plastics:
        if re.search(r'\b' + re.escape(p) + r'\b', combined, re.IGNORECASE):
            found['materials']['plastics'].add(p)
    
    for m in metals:
        if re.search(r'\b' + re.escape(m) + r'\b', combined, re.IGNORECASE):
            found['materials']['metals'].add(m)
    
    return found

async def scrape_page(url, session):
    """Scrape a single page"""
    try:
        response = await session.get(url, timeout=30.0)
        html = response.text
        
        # Extract emails
        emails = EMAIL_REGEX.findall(html)
        emails = [e.lower() for e in emails if is_valid_email(e)]
        
        # Detect manufacturing data
        indicators = detect_manufacturing_indicators(html, url)
        
        return {
            'url': url,
            'html': html,
            'emails': set(emails),
            'indicators': indicators
        }
    except Exception as e:
        print(f"  ❌ {url}: {str(e)[:30]}")
        return None

async def crawl_business(base_url):
    """Crawl entire business website"""
    if not base_url.startswith('http'):
        base_url = f'https://{base_url}'
    
    domain = urlparse(base_url).netloc.replace('www.', '')
    
    async with httpx.AsyncClient(follow_redirects=True) as session:
        # Step 1: Fetch homepage
        print(f"\n🔍 Crawling {domain}...")
        homepage = await scrape_page(base_url, session)
        
        if not homepage:
            return create_error_result(base_url, domain)
        
        # Step 2: Extract internal links
        internal_links = extract_internal_links(homepage['html'], domain)
        print(f"  📄 Found {len(internal_links)} internal pages")
        
        # Step 3: Scrape all pages (limit to 20 for speed)
        pages_to_scrape = internal_links[:20]
        tasks = [scrape_page(link, session) for link in pages_to_scrape]
        results = await asyncio.gather(*tasks)
        
        # Add homepage to results
        all_pages = [homepage] + [r for r in results if r]
        
        # Step 4: Aggregate data across all pages
        aggregated = {
            'domain': domain,
            'emails': set(),
            'equipment_types': set(),
            'brands': set(),
            'keywords': set(),
            'plastics': set(),
            'metals': set(),
            'pages_scraped': len(all_pages)
        }
        
        for page in all_pages:
            if page:
                aggregated['emails'].update(page['emails'])
                aggregated['equipment_types'].update(page['indicators']['equipment_types'])
                aggregated['brands'].update(page['indicators']['brands'])
                aggregated['keywords'].update(page['indicators']['keywords'])
                aggregated['plastics'].update(page['indicators']['materials']['plastics'])
                aggregated['metals'].update(page['indicators']['materials']['metals'])
        
        total_matches = (
            len(aggregated['equipment_types']) +
            len(aggregated['brands']) +
            len(aggregated['keywords']) +
            len(aggregated['plastics']) +
            len(aggregated['metals'])
        )
        
        print(f"  ✅ {len(aggregated['emails'])} emails | {total_matches} manufacturing matches")
        
        return {
            'url': base_url,
            'domain': domain,
            'emails': list(aggregated['emails']) if aggregated['emails'] else None,
            'equipment_types': list(aggregated['equipment_types']) if aggregated['equipment_types'] else None,
            'brands': list(aggregated['brands']) if aggregated['brands'] else None,
            'keywords': list(aggregated['keywords']) if aggregated['keywords'] else None,
            'plastics': list(aggregated['plastics']) if aggregated['plastics'] else None,
            'metals': list(aggregated['metals']) if aggregated['metals'] else None,
            'total_matches': total_matches,
            'pages_scraped': aggregated['pages_scraped'],
            'enrichment_status': 'completed' if aggregated['emails'] else 'no_email',
            'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def create_error_result(url, domain):
    """Create error result"""
    return {
        'url': url,
        'domain': domain,
        'emails': None,
        'equipment_types': None,
        'brands': None,
        'keywords': None,
        'plastics': None,
        'metals': None,
        'total_matches': 0,
        'pages_scraped': 0,
        'enrichment_status': 'error',
        'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def main():
    df = pd.read_csv('businesses.csv')
    urls = df['url'].tolist()
    
    print(f"🚀 MULTI-PAGE MANUFACTURING CRAWLER")
    print(f"📊 Processing {len(urls)} businesses")
    print(f"⚡ Up to 20 pages per business\n")
    
    # Crawl businesses (limit concurrency to avoid overwhelming)
    semaphore = asyncio.Semaphore(10)  # 10 businesses at once
    
    async def crawl_with_limit(url):
        async with semaphore:
            return await crawl_business(url)
    
    tasks = [crawl_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Write to CSV
    fieldnames = [
        'url', 'domain', 'emails', 'equipment_types', 'brands',
        'keywords', 'plastics', 'metals', 'total_matches',
        'pages_scraped', 'enrichment_status', 'scraped_at'
    ]
    
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            row = r.copy()
            for key in ['emails', 'equipment_types', 'brands', 'keywords', 'plastics', 'metals']:
                if row[key]:
                    row[key] = ', '.join(row[key])
            writer.writerow(row)
    
    success = len([r for r in results if r['emails']])
    total_pages = sum(r['pages_scraped'] for r in results)
    
    print(f"\n🎉 COMPLETE!")
    print(f"📧 Businesses with emails: {success}")
    print(f"📄 Total pages scraped: {total_pages}")
    print(f"📁 Results: scraped_data.csv")

if __name__ == "__main__":
    asyncio.run(main())