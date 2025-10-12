"""
Quick test to verify Supabase connection works
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
    
    # Test query - get pending domains
    response = supabase.table('domain_enrich').select('domain').eq('enrichment_status', 'pending').limit(5).execute()
    
    pending_count = len(response.data) if response.data else 0
    
    print(f"✅ Connected to Supabase successfully!")
    print(f"📊 Found at least {pending_count} pending domains (showing first 5)")
    
    if response.data:
        print(f"\n📝 Sample domains:")
        for i, row in enumerate(response.data[:5], 1):
            print(f"   {i}. {row['domain']}")
    else:
        print(f"\n⚠️  No pending domains found!")
        print(f"   Make sure you have domains with enrichment_status='pending'")
    
    print(f"\n🚀 Ready to run the scraper!")
    print(f"   Run: python main_fixed.py")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print(f"\nTroubleshooting:")
    print(f"1. Check your SUPABASE_URL is correct")
    print(f"2. Check your SUPABASE_KEY is correct")
    print(f"3. Verify the 'domain_enrich' table exists")

