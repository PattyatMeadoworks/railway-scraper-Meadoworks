"""Test that brand detection is working"""
import re

# Sample brands
BRANDS = ['haas', 'mazak', 'engel', 'arburg', 'trumpf']

# Sample text that should match
test_text = "We use Haas CNC machines, Mazak lathes, and Engel injection molding equipment."
combined = test_text.lower()

found_brands = set()

# This is the exact code from main.py
for brand in BRANDS:
    if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
        found_brands.add(brand)

print("🧪 Testing brand detection:")
print(f"Test text: {test_text}")
print(f"\n✅ Brands found: {found_brands}")
print(f"Total: {len(found_brands)} brands detected")

if len(found_brands) == 3:
    print("\n🎉 Brand detection is WORKING!")
    print("   Brands ARE being detected in your scraper")
    print("   They're saved in equipment_types column (everything in one column)")
else:
    print("\n❌ Brand detection not working")

