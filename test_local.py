"""
Quick local test script to verify the scraper logic works
Tests URL variations and keyword detection without hitting the database
"""
import asyncio
import httpx
from datetime import datetime

# Sample manufacturing terms for testing
TEST_TERMS = ['cnc', 'machining', 'injection molding', 'laser cutting', 'welding']
TEST_BRANDS = ['haas', 'mazak', 'engel', 'trumpf']

# Test domains
TEST_DOMAINS = [
    'example.com',           # Should work (but no keywords expected)
    'google.com',            # Should work (but no keywords expected)
    'thisdoesnotexist123456789.com',  # Should fail (timeout)
]

async def test_url_variations(domain):
    """Test if we can connect to a domain"""
    clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    
    url_variations = [
        f'https://{clean_domain}',
        f'https://www.{clean_domain}',
        f'http://{clean_domain}',
        f'http://www.{clean_domain}',
    ]
    
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={'User-Agent': 'Mozilla/5.0'}
    ) as session:
        for url in url_variations:
            try:
                print(f"  Trying: {url}")
                response = await session.get(url, timeout=10.0)
                if response.status_code < 400:
                    print(f"  ✅ SUCCESS: {url} (status: {response.status_code})")
                    return True, response.text
            except Exception as e:
                print(f"  ❌ Failed: {type(e).__name__}")
                continue
    
    print(f"  ❌ All variations failed")
    return False, None

def detect_keywords(html):
    """Simple keyword detection test"""
    if not html:
        return []
    
    text = html.lower()
    found = []
    
    for term in TEST_TERMS:
        if term in text:
            found.append(term)
    
    for brand in TEST_BRANDS:
        if brand in text:
            found.append(f"[brand] {brand}")
    
    return found

async def main():
    print("🧪 Testing Scraper Logic (No Database Required)\n")
    print("="*60)
    
    for domain in TEST_DOMAINS:
        print(f"\n🔍 Testing: {domain}")
        start = datetime.now()
        success, html = await test_url_variations(domain)
        elapsed = (datetime.now() - start).total_seconds()
        
        if success and html:
            keywords = detect_keywords(html)
            print(f"  ⏱️  Time: {elapsed:.1f}s")
            print(f"  📊 Result: SUCCESS")
            if keywords:
                print(f"  🔑 Keywords found: {keywords}")
            else:
                print(f"  📭 No manufacturing keywords (expected for test sites)")
        else:
            print(f"  ⏱️  Time: {elapsed:.1f}s")
            print(f"  📊 Result: FAILED (domain unreachable)")
    
    print("\n" + "="*60)
    print("✅ Local test complete!")
    print("\nTo test with your Supabase database:")
    print("1. Create local.env file with your credentials:")
    print("   SUPABASE_URL=https://your-project.supabase.co")
    print("   SUPABASE_KEY=your-anon-key")
    print("2. Run: python test_supabase_connection.py")
    print("3. Run: python main.py")

if __name__ == "__main__":
    asyncio.run(main())
