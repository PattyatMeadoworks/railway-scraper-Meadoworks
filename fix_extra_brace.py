"""Remove extra closing brace on line 927"""

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 927 (index 926) has extra }
if lines[926].strip() == '}':
    print(f"Found extra brace on line 927: '{lines[926].strip()}'")
    lines[926] = ''  # Remove it
    print("✅ Removed extra closing brace")

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed syntax error!")

