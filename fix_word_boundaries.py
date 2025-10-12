"""Fix the word boundary regex that got broken"""

content = open('main.py', 'r', encoding='utf-8').read()

# Fix brands regex
content = content.replace(
    "if re.search(r'' + re.escape(brand) + r'', combined, re.IGNORECASE):",
    "if re.search(r'\\b' + re.escape(brand) + r'\\b', combined, re.IGNORECASE):"
)

# Fix plastics regex
content = content.replace(
    "if re.search(r'' + re.escape(p) + r'', combined, re.IGNORECASE):",
    "if re.search(r'\\b' + re.escape(p) + r'\\b', combined, re.IGNORECASE):"
)

# Fix metals regex
content = content.replace(
    "if re.search(r'' + re.escape(m) + r'', combined, re.IGNORECASE):",
    "if re.search(r'\\b' + re.escape(m) + r'\\b', combined, re.IGNORECASE):"
)

open('main.py', 'w', encoding='utf-8').write(content)

print("✅ Fixed word boundary regex for brands, plastics, and metals!")
print("   Now brands will be detected properly")

