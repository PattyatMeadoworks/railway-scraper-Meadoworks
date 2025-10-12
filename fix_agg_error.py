"""Fix the 'agg is not defined' error"""

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the problematic lines
for i in range(len(lines)):
    # Remove duplicate total_matches calculation that references agg
    if "total_matches = sum([len(agg[k]) for k in" in lines[i]:
        print(f"Line {i+1}: Removing duplicate total_matches using agg")
        lines[i] = ''  # Remove this line
    
    # Fix log line that references agg['emails']
    if "len(agg['emails'])" in lines[i]:
        print(f"Line {i+1}: Replacing agg['emails'] with all_emails")
        lines[i] = lines[i].replace("agg['emails']", "all_emails")

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Fixed 'agg is not defined' error!")
print("   • Removed duplicate total_matches calculation")
print("   • Changed agg['emails'] to all_emails")

