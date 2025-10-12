"""
Analyze overlap between EQUIPMENT_TYPES and KEYWORDS
Then create consolidated list with Spanish translations
"""

# Current lists from main.py (simplified for analysis)
equipment_sample = ['cnc machining', 'injection molding', 'laser cutting', '3d printing', 'welding']
keywords_sample = ['cnc', 'machining', 'molding', 'laser', 'welding']

# Check overlap
overlap = set()
for eq in equipment_sample:
    for kw in keywords_sample:
        if kw in eq or eq in kw:
            overlap.add((eq, kw))

print("🔍 Sample Overlap Found:")
for eq, kw in list(overlap)[:5]:
    print(f"   Equipment: '{eq}' contains Keyword: '{kw}'")

print("\n💡 Solution: Merge into single MANUFACTURING_TERMS list")
print("   Benefits:")
print("   • No duplicate checking")
print("   • Simpler code")
print("   • Easier to maintain")
print("   • Add Spanish translations")

# Spanish translations for common manufacturing terms
spanish_terms = {
    # Molding
    'molding': 'moldeo',
    'molded': 'moldeado', 
    'injection molding': 'moldeo por inyección',
    'blow molding': 'moldeo por soplado',
    'thermoforming': 'termoformado',
    'rotomolding': 'rotomoldeo',
    
    # Machining
    'machining': 'mecanizado',
    'machined': 'mecanizada',
    'cnc': 'cnc',
    'milling': 'fresado',
    'turning': 'torneado',
    'lathe': 'torno',
    
    # Welding
    'welding': 'soldadura',
    'welded': 'soldado',
    'welder': 'soldador',
    
    # Casting
    'casting': 'fundición',
    'die casting': 'fundición a presión',
    
    # Extrusion
    'extrusion': 'extrusión',
    'extruded': 'extruido',
    
    # Fabrication
    'fabrication': 'fabricación',
    'fabricated': 'fabricado',
    
    # Cutting
    'laser cutting': 'corte láser',
    'waterjet cutting': 'corte por chorro de agua',
    
    # Materials
    'plastic': 'plástico',
    'metal': 'metal',
    'aluminum': 'aluminio',
    'steel': 'acero',
    'stainless steel': 'acero inoxidable',
}

print(f"\n🌎 Spanish Terms to Add: {len(spanish_terms)}")
print("\n📋 Sample Spanish Terms:")
for eng, spa in list(spanish_terms.items())[:10]:
    print(f"   {eng} → {spa}")

print("\n✅ Ready to generate consolidated list with Spanish!")

