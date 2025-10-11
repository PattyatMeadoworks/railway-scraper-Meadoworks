import asyncio
import httpx
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import sys

# ===== SUPABASE CREDENTIALS FROM ENV =====
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# MANUFACTURING EQUIPMENT & MATERIALS DETECTOR v7.0
EQUIPMENT_TYPES = [
    '5-axis machining', '4-axis machining', '3-axis machining', 'multi-axis machining',
    'cnc machining services', 'cnc machining capabilities', 'precision machining',
    'cnc turning', 'cnc turning services', 'cnc milling', 'cnc milling services',
    'swiss machining', 'swiss-type machining', 'vertical machining center',
    'laser cutting', 'laser cutting services', 'fiber laser cutting',
    'waterjet cutting', 'press brake', 'metal forming', 'bending services',
    'sheet metal fabrication', 'metal fabrication', 'welding', 'mig welding', 'tig welding',
    'wire edm', 'sinker edm', 'grinding', 'precision grinding',
    'metal stamping', 'progressive die stamping', 'tool and die',
    'die casting', 'investment casting', 'sand casting',
    'injection molding', 'plastic injection molding', 'insert molding', 'overmolding',
    'two-shot molding', '2k molding', 'lsr molding', 'micro molding',
    'extrusion', 'plastic extrusion', 'blow molding', 'thermoforming',
    'rotomolding', 'compression molding', '3d printing', 'additive manufacturing'
]

BRANDS = [
    'haas', 'mazak', 'dmg mori', 'okuma', 'makino', 'fanuc', 'brother',
    'doosan', 'hermle', 'chiron', 'trumpf', 'amada', 'bystronic', 'prima power',
    'omax', 'jet edge', 'accurpress', 'ermaksan', 'miller', 'lincoln electric',
    'sodick', 'charmilles', 'engel', 'arburg', 'haitian', 'sumitomo demag', 'nissei',
    'husky', 'milacron', 'krauss maffei', 'boy', 'chen hsong', 'davis-standard',
    'coperion', 'battenfeld-cincinnati', 'kautex', 'bekum', 'uniloy', 'jomar',
    'sidel', 'brown machine', 'illig', 'kiefel', 'persico', 'ferry', 'stratasys',
    '3d systems', 'eos', 'formlabs', 'novatec', 'motan', 'maguire', 'matsui', 'piovan'
]

PLASTICS = [
    'pet', 'hdpe', 'ldpe', 'pp', 'polypropylene', 'pvc', 'abs', 'nylon', 'polyamide',
    'pa6', 'pa66', 'pc', 'polycarbonate', 'lexan', 'pom', 'acetal', 'delrin',
    'petg', 'peek', 'ultem', 'pei', 'pps', 'ryton', 'ptfe', 'teflon',
    'tpe', 'tpu', 'lsr', 'liquid silicone rubber', 'rpet', 'recycled pet'
]

METALS = [
    'aluminum', '6061', '6061-t6', '7075', '7075-t6', '5052', '2024',
    'carbon steel', 'alloy steel', '4140', '4340', '1018', '1045',
    'stainless steel', '304', '316', '303', '17-4', '17-4 ph',
    '304l', '316l', 'duplex stainless', 'brass', 'bronze', 'copper',
    'titanium', 'ti-6al-4v', 'inconel', 'hastelloy', 'monel'
]

KEYWORDS = [
    'cnc', 'machining', 'machine shop', 'mill', 'lathe', 'turning', 'milling',
    'laser', 'laser cutting', 'waterjet', 'press brake', 'bending', 'welding',
    'edm', 'grinding', 'stamping', 'casting', 'die casting',
    'injection molding', 'plastic injection', 'extrusion', 'blow molding',
    'thermoforming', '3d printing', 'additive manufacturing'
]

EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,})\b', re.IGNORECASE)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    sys.stdout.flush()

def is_valid_email(email):
    if email.count('@') != 1:
        return False
    invalid = ['.png', '.jpg', '.css', '.js', 'example.com', 'noreply', 'sentry.io']
    return not any(p in email.lower() for p in invalid)

def extract_internal_links(html, base_domain):
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
    
    return list(set(links))[:20]

def detect_manufacturing(html, url):
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
    try:
        response = await session.get(url, timeout=10.0)
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

async def crawl_and_update_domain(record):
    domain = record['domain']
    record_id = record['id']
    
    base_url = domain if domain.startswith('http') else f'https://{domain}'
    clean_domain = urlparse(base_url).netloc.replace('www.', '')
    
    log(f"🔍 Crawling {clean_domain}")
    
    async with httpx.AsyncClient(follow_redirects=True) as session:
        homepage = await scrape_page(base_url, session)
        
        if not homepage:
            log(f"  ❌ Failed to load {clean_domain}")
            return
        
        internal_links = extract_internal_links(homepage['html'], clean_domain)
        log(f"  📄 Found {len(internal_links)} pages to crawl")
        
        tasks = [scrape_page(link, session) for link in internal_links]
        results = await asyncio.gather(*tasks)
        
        all_pages = [homepage] + [r for r in results if r]
        
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
        
        update_data = {
            'emails': list(agg['emails']) if agg['emails'] else [],
            'equipment_types': list(agg['equipment']) if agg['equipment'] else [],
            'brands': list(agg['brands']) if agg['brands'] else [],
            'keywords': list(agg['keywords']) if agg['keywords'] else [],
            'materials': {
                'plastics': list(agg['plastics']) if agg['plastics'] else [],
                'metals': list(agg['metals']) if agg['metals'] else []
            },
            'enrichment_status': 'completed',
            'enrichment_message': f'Scraped {len(all_pages)} pages, found {len(agg["emails"])} emails',
            'last_scraped_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'source_url': base_url
        }
        
        try:
            supabase.table('domain_enrich').update(update_data).eq('id', record_id).execute()
            log(f"  💾 Saved to Supabase")
        except Exception as e:
            log(f"  ❌ Error saving: {str(e)}")

async def main():
    log("🚀 DOMAIN ENRICHMENT SCRAPER - SUPABASE MODE")
    log(f"📅 Started at {datetime.utcnow().isoformat()}\n")
    
    total_processed = 0
    batch_number = 0
    
    while True:
        batch_number += 1
        log(f"\n{'='*60}")
        log(f"📦 BATCH {batch_number}")
        log(f"{'='*60}\n")
        
        try:
            log("📡 Fetching pending domains from Supabase...")
            response = supabase.table('domain_enrich').select('*').eq('enrichment_status', 'pending').limit(500).execute()
            records = response.data
            
            if not records:
                log(f"\n✅ NO MORE PENDING DOMAINS!")
                log(f"🎉 TOTAL PROCESSED: {total_processed} domains")
                break
                
            log(f"📊 Found {len(records)} pending domains in this batch\n")
        except Exception as e:
            log(f"❌ Error fetching domains: {str(e)}")
            break
        
        semaphore = asyncio.Semaphore(100)
        
        async def crawl_with_limit(record):
            async with semaphore:
                return await crawl_and_update_domain(record)
        
        log("🏭 Starting crawl...\n")
        tasks = [crawl_with_limit(r) for r in records]
        await asyncio.gather(*tasks)
        
        total_processed += len(records)
        log(f"\n✅ Batch {batch_number} complete!")
        log(f"📊 Batch: {len(records)} domains | Total so far: {total_processed} domains")
        
        await asyncio.sleep(2)
    
    log(f"\n{'='*60}")
    log(f"🎉 ALL DONE!")
    log(f"📊 TOTAL PROCESSED: {total_processed} domains")
    log(f"📦 Total batches: {batch_number}")
    log(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())