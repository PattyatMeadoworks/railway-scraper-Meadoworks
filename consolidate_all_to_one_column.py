"""
Consolidate ALL terms into equipment_types column
Puts brands, plastics, metals, manufacturing terms all together
"""

print("📝 Reading main.py...")
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the aggregation section
new_lines = []
in_agg_section = False
in_result_section = False
skip_until_line = None

for i, line in enumerate(lines):
    # Skip lines if we're in a section we're replacing
    if skip_until_line and i < skip_until_line:
        continue
    elif skip_until_line and i >= skip_until_line:
        skip_until_line = None
    
    # Find aggregation section
    if '# Aggregate results' in line and 'agg = {' in lines[i+1] if i+1 < len(lines) else False:
        # Replace entire aggregation section
        new_lines.append('    # Aggregate results - EVERYTHING in ONE column!\n')
        new_lines.append('    all_matches = set()\n')
        new_lines.append('    all_emails = set()\n')
        new_lines.append('    \n')
        new_lines.append('    for page in all_pages:\n')
        new_lines.append('        if page:\n')
        new_lines.append('            all_emails.update(page[\'emails\'])\n')
        new_lines.append('            # Combine EVERYTHING into one set - brands, terms, materials!\n')
        new_lines.append('            all_matches.update(page[\'indicators\'][\'manufacturing_terms\'])\n')
        new_lines.append('            all_matches.update(page[\'indicators\'][\'brands\'])\n')
        new_lines.append('            all_matches.update(page[\'indicators\'][\'plastics\'])\n')
        new_lines.append('            all_matches.update(page[\'indicators\'][\'metals\'])\n')
        new_lines.append('    \n')
        new_lines.append('    total_matches = len(all_matches)\n')
        new_lines.append('    \n')
        # Skip original agg section (next ~16 lines)
        skip_until_line = i + 17
        continue
    
    # Find result dictionary section
    if 'result = {' in line and "'domain': domain," in lines[i+1] if i+1 < len(lines) else False:
        # Replace result section
        new_lines.append('    result = {\n')
        new_lines.append('        \'domain\': domain,\n')
        new_lines.append('        \'emails\': list(all_emails),\n')
        new_lines.append('        \'equipment_types\': list(all_matches),  # ALL terms in one column!\n')
        new_lines.append('        \'brands\': [],  # Empty - consolidated into equipment_types\n')
        new_lines.append('        \'keywords\': [],  # Empty - consolidated into equipment_types\n')
        new_lines.append('        \'materials\': {\'plastics\': [], \'metals\': []},  # Empty - consolidated\n')
        new_lines.append('        \'enrichment_status\': \'completed\' if all_emails else \'no_email\',\n')
        new_lines.append('        \'last_scraped_at\': datetime.now().isoformat()\n')
        new_lines.append('    }\n')
        # Skip original result section (next ~11 lines)
        skip_until_line = i + 12
        continue
    
    new_lines.append(line)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Consolidated ALL data into equipment_types column!")
print("📊 Now saves:")
print("   • equipment_types: [ALL brands, terms, plastics, metals combined]")
print("   • brands: [] (empty)")
print("   • keywords: [] (empty)")
print("   • materials: {plastics: [], metals: []} (empty)")
print("\n🎯 Benefits:")
print("   • One column to search!")
print("   • Simpler database structure")
print("   • Faster queries")
print("   • Easier to filter/search later")

