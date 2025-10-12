"""
Replace the entire detect_manufacturing function with working version
"""

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The correct detect_manufacturing function
correct_function = """def detect_manufacturing(html, url):
    \"\"\"Detect manufacturing capabilities - Now with Spanish support!\"\"\"
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text().lower()
    combined = text + ' ' + url.lower()
    
    found = {
        'manufacturing_terms': set(),
        'brands': set(),
        'plastics': set(),
        'metals': set()
    }
    
    # Search manufacturing terms (simple string search)
    for term in MANUFACTURING_TERMS:
        if term in combined:
            found['manufacturing_terms'].add(term)
    
    # Search brands (with word boundaries) - FIXED!
    for brand in BRANDS:
        if re.search(r'\\\\b' + re.escape(brand) + r'\\\\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    # Search plastics (with word boundaries) - FIXED!
    for p in PLASTICS:
        if re.search(r'\\\\b' + re.escape(p) + r'\\\\b', combined, re.IGNORECASE):
            found['plastics'].add(p)
    
    # Search metals (with word boundaries) - FIXED!
    for m in METALS:
        if re.search(r'\\\\b' + re.escape(m) + r'\\\\b', combined, re.IGNORECASE):
            found['metals'].add(m)
    
    return found"""

# Find and replace the function
import re
pattern = r'def detect_manufacturing\(html, url\):.*?return found'
content = re.sub(pattern, correct_function, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Replaced detect_manufacturing function with working version!")
print("✅ Word boundaries now properly set as r'\\b'")
print("✅ Brands, plastics, and metals will now be detected!")

