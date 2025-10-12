content = open('main.py', 'r', encoding='utf-8').read()
content = content.replace('TABLE_NAME = "domain_enrich_duplicate"', 'TABLE_NAME = "domain_enrich_duplicate_duplicate"')
open('main.py', 'w', encoding='utf-8').write(content)
print('✅ Updated TABLE_NAME to: domain_enrich_duplicate_duplicate')

