import re

print("🔧 Fixing word boundary regex in main.py...")

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken regex patterns - need to escape the backslash properly
# The pattern r'' + re.escape(brand) + r'' should be r'\b' + re.escape(brand) + r'\b'

content = content.replace(
    "re.search(r'' + re.escape(brand) + r'', combined, re.IGNORECASE)",
    "re.search(r'\\b' + re.escape(brand) + r'\\b', combined, re.IGNORECASE)"
)

content = content.replace(
    "re.search(r'' + re.escape(p) + r'', combined, re.IGNORECASE)",
    "re.search(r'\\b' + re.escape(p) + r'\\b', combined, re.IGNORECASE)"
)

content = content.replace(
    "re.search(r'' + re.escape(m) + r'', combined, re.IGNORECASE)",
    "re.search(r'\\b' + re.escape(m) + r'\\b', combined, re.IGNORECASE)"
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed! Word boundaries restored for:")
print("   • BRANDS detection (Haas, Mazak, Engel, etc.)")
print("   • PLASTICS detection (ABS, nylon, PEEK, etc.)")
print("   • METALS detection (aluminum, steel, etc.)")
print("\n🎯 Brands will now be detected properly!")

