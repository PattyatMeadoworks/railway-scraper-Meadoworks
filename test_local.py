"""
Quick local test script to verify the scraper works
Tests a few domains without hitting the full database
"""
import asyncio
import httpx
from datetime import datetime

# Test domains (mix of good and bad)
TEST_DOMAINS = [
    'example.com',           # Should work
    'google.com',            # Should work
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
                    return True
            except Exception as e:
                print(f"  ❌ Failed: {type(e).__name__}")
                continue
    
    print(f"  ❌ All variations failed")
    return False

async def main():
    print("🧪 Testing URL Variation Logic (No Database Required)\n")
    print("="*60)
    
    for domain in TEST_DOMAINS:
        print(f"\n🔍 Testing: {domain}")
        start = datetime.now()
        success = await test_url_variations(domain)
        elapsed = (datetime.now() - start).total_seconds()
        print(f"  ⏱️  Time: {elapsed:.1f}s")
        print(f"  📊 Result: {'SUCCESS' if success else 'FAILED'}")
    
    print("\n" + "="*60)
    print("✅ Local test complete!")
    print("\nTo test with Supabase:")
    print("1. Set environment variables:")
    print("   $env:SUPABASE_URL='https://your-project.supabase.co'")
    print("   $env:SUPABASE_KEY='your-anon-key'")
    print("2. Run: python main_fixed.py")

if __name__ == "__main__":
    asyncio.run(main())

