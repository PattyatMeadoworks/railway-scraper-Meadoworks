"""
Quick test to verify Supabase connection and check domain counts
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load credentials
load_dotenv('local.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("🔍 Testing Supabase Connection...")
print(f"📡 URL: {SUPABASE_URL}")
print(f"🔑 Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "❌ No key found")
print()

try:
    # Initialize client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized")
    
    # Get total domain count
    total_response = supabase.table('domains').select('domain', count='exact').limit(1).execute()
    total_count = total_response.count if hasattr(total_response, 'count') else 'unknown'
    
    # Get pending domains count
    pending_response = supabase.table('domains').select('domain').or_(
        'website_scrape_status.eq.pending,website_scrape_status.is.null'
    ).limit(5).execute()
    pending_sample = pending_response.data
    
    # Get completed domains count
    completed_response = supabase.table('domains').select('domain').eq(
        'website_scrape_status', 'completed'
    ).limit(1).execute()
    
    print(f"\n✅ Connected to Supabase successfully!")
    print(f"\n📊 Domain Statistics:")
    print(f"   Total domains: {total_count}")
    print(f"   Pending to scrape: {len(pending_sample)}+ (showing first 5)")
    
    if pending_sample:
        print(f"\n📝 Sample pending domains:")
        for i, row in enumerate(pending_sample[:5], 1):
            print(f"   {i}. {row['domain']}")
    else:
        print(f"\n⚠️  No pending domains found!")
        print(f"   All domains may already be scraped.")
    
    print(f"\n🚀 Ready to run the scraper!")
    print(f"   Run: python main.py")
    print(f"   Or for continuous mode: python main.py --continuous")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print(f"\nTroubleshooting:")
    print(f"1. Check your SUPABASE_URL is correct")
    print(f"2. Check your SUPABASE_KEY is correct")
    print(f"3. Verify the 'domains' table exists")
    print(f"4. Make sure you've added the website_* columns")
