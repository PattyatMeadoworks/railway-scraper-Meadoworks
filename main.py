import asyncio
import httpx
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime
from urllib.parse import urlparse
import sys
import pandas as pd

# Complete equipment types and phrases
EQUIPMENT_TYPES = [
    'cnc machining', 'laser cutting', 'waterjet cutting', 'injection molding',
    'extrusion', 'blow molding', 'thermoforming', 'rotational molding',
    'compression molding', 'tube bending', 'pipe fabrication', 'metal stamping',
    'die casting', 'investment casting', 'sand casting', 'welding',
    'powder coating', 'anodizing', 'plating', 'heat treating'
]

# Equipment brands
BRANDS = [
    'haas', 'mazak', 'okuma', 'dmg mori', 'makino', 'fanuc', 'brother',
    'engel', 'arburg', 'husky', 'milacron', 'cincinnati', 'trumpf',
    'amada', 'bystronic', 'prima power', 'doosan', 'hyundai wia'
]

# Materials
PLASTICS = ['abs', 'nylon', 'polycarbonate', 'pet', 'hdpe', 'ldpe', 'pp', 'pvc', 'peek', 'ultem']
METALS = ['aluminum', 'stainless steel', 'steel', 'brass', 'copper', 'titanium', '6061', '7075', '304', '316']

# Keywords
KEYWORDS = ['cnc', 'laser', 'welding', 'molding', 'fabrication', 'machining', 'casting', 'stamping']

# Email regex
EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,})\b', re.IGNORECASE)

def log(msg):
    """Print with timestamp and flush immediately"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    sys.stdout.flush()

def is_valid_email(email):
    """Validate email"""
    if email.count('@') != 1:
        return False
    invalid = ['.png', '.jpg', '.css', '.js', 'example.com', 'noreply', 'sentry.io']
    return not any(p in email.lower() for p in invalid)

def extract_internal_links(html, base_domain):
    """Extract internal links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        
        if href.startswith('/'):
            url = f'https://{base_domain}{href}'
        elif href.startswith('http'):
            url = href
        else:
            continue
        
        try:
            parsed = urlparse(url)
            link_domain = parsed.netloc.replace('www.', '')
            
            if link_domain == base_domain.replace('www.', ''):
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                links.append(clean_url)
        except:
            continue
    
    return list(set(links))[:15]  # Max 15 pages per site

def detect_manufacturing(html, url):
    """Detect manufacturing indicators"""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text().lower()
    combined = text + ' ' + url.lower()
    
    found = {
        'equipment': set(),
        'brands': set(),
        'keywords': set(),
        'plastics': set(),
        'metals': set()
    }
    
    for eq in EQUIPMENT_TYPES:
        if eq in combined:
            found['equipment'].add(eq)
    
    for brand in BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    for kw in KEYWORDS:
        if kw in combined:
            found['keywords'].add(kw)
    
    for p in PLASTICS:
        if re.search(r'\b' + re.escape(p) + r'\b', combined, re.IGNORECASE):
            found['plastics'].add(p)
    
    for m in METALS:
        if re.search(r'\b' + re.escape(m) + r'\b', combined, re.IGNORECASE):
            found['metals'].add(m)
    
    return found

async def scrape_page(url, session):
    """Scrape single page"""
    try:
        response = await session.get(url, timeout=20.0)
        html = response.text
        
        emails = EMAIL_REGEX.findall(html)
        emails = set([e.lower() for e in emails if is_valid_email(e)])
        
        indicators = detect_manufacturing(html, url)
        
        return {
            'url': url,
            'html': html,
            'emails': emails,
            'indicators': indicators
        }
    except Exception as e:
        return None

async def crawl_business(base_url):
    """Crawl entire business website"""
    if not base_url.startswith('http'):
        base_url = f'https://{base_url}'
    
    domain = urlparse(base_url).netloc.replace('www.', '')
    log(f"🔍 Crawling {domain}")
    
    async with httpx.AsyncClient(follow_redirects=True) as session:
        # Scrape homepage
        homepage = await scrape_page(base_url, session)
        
        if not homepage:
            log(f"  ❌ Failed to load {domain}")
            return create_error_result(base_url, domain)
        
        # Extract internal links
        internal_links = extract_internal_links(homepage['html'], domain)
        log(f"  📄 Found {len(internal_links)} pages to crawl")
        
        # Scrape all pages
        tasks = [scrape_page(link, session) for link in internal_links]
        results = await asyncio.gather(*tasks)
        
        all_pages = [homepage] + [r for r in results if r]
        
        # Aggregate data
        agg = {
            'emails': set(),
            'equipment': set(),
            'brands': set(),
            'keywords': set(),
            'plastics': set(),
            'metals': set()
        }
        
        for page in all_pages:
            if page:
                agg['emails'].update(page['emails'])
                agg['equipment'].update(page['indicators']['equipment'])
                agg['brands'].update(page['indicators']['brands'])
                agg['keywords'].update(page['indicators']['keywords'])
                agg['plastics'].update(page['indicators']['plastics'])
                agg['metals'].update(page['indicators']['metals'])
        
        total_matches = sum([len(agg[k]) for k in ['equipment', 'brands', 'keywords', 'plastics', 'metals']])
        
        log(f"  ✅ {len(agg['emails'])} emails | {total_matches} matches | {len(all_pages)} pages")
        
        return {
            'url': base_url,
            'domain': domain,
            'emails': ', '.join(agg['emails']) if agg['emails'] else '',
            'equipment_types': ', '.join(agg['equipment']) if agg['equipment'] else '',
            'brands': ', '.join(agg['brands']) if agg['brands'] else '',
            'keywords': ', '.join(agg['keywords']) if agg['keywords'] else '',
            'plastics': ', '.join(agg['plastics']) if agg['plastics'] else '',
            'metals': ', '.join(agg['metals']) if agg['metals'] else '',
            'total_matches': total_matches,
            'pages_scraped': len(all_pages),
            'enrichment_status': 'completed' if agg['emails'] else 'no_email',
            'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def create_error_result(url, domain):
    """Create error result"""
    return {
        'url': url,
        'domain': domain,
        'emails': '',
        'equipment_types': '',
        'brands': '',
        'keywords': '',
        'plastics': '',
        'metals': '',
        'total_matches': 0,
        'pages_scraped': 0,
        'enrichment_status': 'error',
        'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def main():
    """Main scraper"""
    log("🚀 MULTI-PAGE MANUFACTURING CRAWLER - CSV MODE")
    log(f"📅 Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Read businesses from CSV
    try:
        log("📡 Reading businesses.csv...")
        df = pd.read_csv('businesses.csv')
        urls = df['url'].tolist()
        log(f"📊 Found {len(urls)} businesses to process")
    except Exception as e:
        log(f"❌ Error reading businesses.csv: {str(e)}")
        return
    
    # Crawl with concurrency limit
    semaphore = asyncio.Semaphore(5)  # 5 businesses at once
    
    async def crawl_with_limit(url):
        async with semaphore:
            return await crawl_business(url)
    
    log("🏭 Starting crawl...\n")
    tasks = [crawl_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Write to CSV
    log("\n💾 Saving results to scraped_data.csv...")
    fieldnames = [
        'url', 'domain', 'emails', 'equipment_types', 'brands',
        'keywords', 'plastics', 'metals', 'total_matches',
        'pages_scraped', 'enrichment_status', 'scraped_at'
    ]
    
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    success = len([r for r in results if r['emails']])
    total_pages = sum(r['pages_scraped'] for r in results)
    
    log(f"\n🎉 COMPLETE!")
    log(f"✅ Saved {len(results)} results to scraped_data.csv")
    log(f"📧 Companies with emails: {success}")
    log(f"📄 Total pages scraped: {total_pages}")

if __name__ == "__main__":
    asyncio.run(main())