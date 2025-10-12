"""
EXPANDED TERMS - All tenses, variations, and forms
This file contains comprehensive term lists that will be copied into main_optimized.py
"""

# Complete equipment types (500+) - ALL VARIATIONS
EQUIPMENT_TYPES = [
    # CNC Machining - All variations
    '5-axis machining', '5-axis machine', '5-axis machined', '5 axis machining', '5 axis machine',
    '4-axis machining', '4-axis machine', '4-axis machined', '4 axis machining', '4 axis machine',
    '3-axis machining', '3-axis machine', '3-axis machined', '3 axis machining', '3 axis machine',
    'multi-axis machining', 'multi-axis machine', 'multi axis machining',
    'cnc machining', 'cnc machined', 'cnc machine', 'cnc machines',
    'cnc machining services', 'cnc machining capabilities', 
    'precision machining', 'precision machine', 'precision machined',
    'precision machining services',
    'cnc turning', 'cnc turned', 'cnc turn',
    'cnc turning services', 'cnc turning capabilities',
    'cnc milling', 'cnc milled', 'cnc mill',
    'cnc milling services', 'cnc milling capabilities',
    'swiss machining', 'swiss-type machining', 'swiss machined', 'swiss machine',
    'swiss machining services', 'swiss screw machining', 'swiss screw machine',
    'vertical machining center', 'vertical machining centres', 'vmc',
    'horizontal machining center', 'horizontal machining centres', 'hmc',
    'turning services', 'turning service', 'turned', 'turning',
    'milling services', 'milling service', 'milled', 'milling',
    'machining services', 'machining service', 'machined', 'machining',
    'precision turning', 'precision turned',
    'live tooling', 'live tooling capabilities', 'live tool',
    
    # Laser Cutting - All variations
    'laser cutting', 'laser cut', 'laser-cut', 'laser cuts',
    'laser cutting services', 'laser cutting capabilities',
    'fiber laser cutting', 'fiber laser cut', 'fiber laser',
    'fiber laser cutting services',
    'co2 laser cutting', 'co2 laser cut', 'co2 laser',
    'co2 laser cutting services',
    'tube laser cutting', 'tube laser cut', 'tube laser',
    'tube laser cutting services',
    '3d laser cutting', '3d laser cut',
    'laser cutting and fabrication', 'metal laser cutting',
    'laser engraving', 'laser engraved', 'laser engrave',
    'laser marking', 'laser marked', 'laser mark',
    'laser welding', 'laser welded', 'laser weld',
    
    # Waterjet Cutting - All variations
    'waterjet cutting', 'waterjet cut', 'water jet cutting', 'water jet cut',
    'waterjet cutting services', 'waterjet cutting capabilities',
    'abrasive waterjet cutting', 'abrasive waterjet',
    'water jet', 'waterjet',
    
    # Press Brake & Forming - All variations
    'press brake', 'press braking', 'press brakes',
    'press brake services', 'press brake capabilities',
    'metal forming', 'metal formed', 'metal form',
    'metal forming services', 'metal forming capabilities',
    'bending services', 'bending service', 'bent', 'bending', 'bend',
    'cnc bending', 'cnc bent', 'cnc bend',
    'precision bending', 'precision bent', 'precision bend',
    'precision bending services',
    'brake press services', 'brake press',
    'forming', 'formed', 'form',
    
    # Sheet Metal Fabrication - All variations
    'sheet metal fabrication', 'sheet metal fabricated', 'sheet metal fabricate',
    'sheet metal fabrication services',
    'sheet metal services', 'sheet metal', 'sheetmetal',
    'metal fabrication', 'metal fabricated', 'metal fabricate',
    'metal fabrication services',
    'custom metal fabrication', 'custom fabrication',
    'cnc punching', 'cnc punched', 'cnc punch',
    'cnc punching services',
    'turret punching', 'turret punched', 'turret punch',
    'turret punching services',
    'punching capabilities', 'punching', 'punched', 'punch',
    
    # Welding - All variations
    'welding', 'welded', 'weld', 'welds', 'welder',
    'welding services', 'welding capabilities',
    'mig welding', 'mig welded', 'mig weld', 'mig',
    'mig welding services',
    'tig welding', 'tig welded', 'tig weld', 'tig',
    'tig welding services',
    'robotic welding', 'robotic welded', 'robotic weld',
    'robotic welding services', 'robotic welding capabilities',
    'laser welding', 'laser welded', 'laser weld',
    'laser welding services',
    'spot welding', 'spot welded', 'spot weld',
    'arc welding', 'arc welded', 'arc weld',
    'arc welding services',
    'ultrasonic welding', 'ultrasonic welded', 'ultrasonic weld',
    
    # EDM - All variations
    'wire edm', 'wire edm services', 'wire edm capabilities',
    'sinker edm', 'sinker edm services', 'ram edm', 'ram edm services',
    'edm services', 'edm capabilities', 'edm',
    'electrical discharge machining', 'electrical discharge machine',
    
    # Grinding - All variations
    'grinding', 'grind', 'ground', 'grinder', 'grinders',
    'grinding services', 'grinding capabilities',
    'precision grinding', 'precision ground', 'precision grind',
    'precision grinding services',
    'surface grinding', 'surface ground', 'surface grind',
    'surface grinding services',
    'cylindrical grinding', 'cylindrical ground', 'cylindrical grind',
    'cylindrical grinding services',
    'centerless grinding', 'centerless ground', 'centerless grind',
    'centerless grinding services',
    'od grinding', 'id grinding',
    
    # Stamping & Die - All variations
    'metal stamping', 'metal stamped', 'metal stamp',
    'metal stamping services', 'metal stamping capabilities',
    'progressive die stamping', 'progressive die stamped',
    'stamping', 'stamped', 'stamp', 'stamps',
    'stamping services', 'stamping capabilities',
    'tool and die', 'tool & die', 'tooling and die',
    'tool and die services', 'tool and die capabilities',
    'mold making', 'mold made', 'mold maker', 'moldmaking',
    'mold making services',
    'tooling', 'tooled', 'tool', 'tools',
    'tooling services',
    'die making', 'die made', 'die maker',
    'die making services',
    
    # Casting - All variations
    'die casting', 'die cast', 'diecast', 'die-cast',
    'die casting services', 'die casting capabilities',
    'investment casting', 'investment cast',
    'investment casting services',
    'sand casting', 'sand cast',
    'sand casting services',
    'aluminum die casting', 'aluminum die cast',
    'aluminum die casting services',
    'casting', 'cast', 'casted', 'casts',
    'casting services', 'casting capabilities',
    
    # Injection Molding - All variations (THIS IS THE BIG ONE!)
    'injection molding', 'injection molded', 'injection mold', 'injection moulding', 'injection moulded',
    'injection molding services', 'injection molding capabilities',
    'custom injection molding', 'custom injection molded',
    'contract molding', 'contract molded',
    'contract molding services',
    'plastic injection molding', 'plastic injection molded',
    'plastic injection', 'plastic molding', 'plastic molded', 'plastic mold',
    'insert molding', 'insert molded', 'insert mold',
    'insert molding services', 'insert molding capabilities',
    'overmolding', 'overmolded', 'overmold', 'over-molding', 'over-molded',
    'overmolding services', 'overmolding capabilities',
    'two-shot molding', 'two-shot molded', 'two shot molding', 'two shot molded',
    'two-shot molding services', 'two-shot injection molding',
    '2k molding', '2k molded', '2-shot molding', '2-shot molded', '2 shot molding',
    'multi-component molding', 'multi-component molded',
    'multi-shot molding', 'multi-shot molded',
    'lsr molding', 'lsr molded', 'lsr mold',
    'lsr molding services',
    'liquid silicone rubber molding', 'liquid silicone rubber molded',
    'micro molding', 'micro molded', 'micro mold',
    'micro molding services',
    'molding', 'molded', 'mold', 'molds', 'moulding', 'moulded',
    'imm', 'injection molding machine', 'injection molding machines',
    
    # Extrusion - All variations
    'extrusion', 'extruded', 'extrude', 'extrudes', 'extruder', 'extruders',
    'extrusion services', 'extrusion capabilities',
    'profile extrusion', 'profile extruded', 'profile extrude',
    'profile extrusion services',
    'pipe extrusion', 'pipe extruded', 'pipe extrude',
    'pipe extrusion services',
    'sheet extrusion', 'sheet extruded', 'sheet extrude',
    'sheet extrusion services',
    'plastic extrusion', 'plastic extruded', 'plastic extrude',
    'plastic extrusion services',
    'blown film', 'blown film extrusion', 'blown film extruded',
    'co-extrusion', 'coextrusion', 'co-extruded', 'coextruded',
    'co-extrusion services',
    
    # Blow Molding - All variations
    'blow molding', 'blow molded', 'blow mold', 'blow moulding', 'blow moulded',
    'blow molding services', 'blow molding capabilities',
    'extrusion blow molding', 'extrusion blow molded',
    'extrusion blow molding services',
    'injection blow molding', 'injection blow molded',
    'injection blow molding services',
    'stretch blow molding', 'stretch blow molded',
    'stretch blow molding services',
    'pet blow molding', 'pet blow molded',
    'bottle manufacturing', 'bottle manufactured', 'bottle maker',
    
    # Thermoforming - All variations (YOUR EXAMPLE!)
    'thermoforming', 'thermoformed', 'thermoform', 'thermoforms',
    'thermo-forming', 'thermo-formed', 'thermo forming', 'thermo formed',
    'thermoforming services', 'thermoforming capabilities',
    'vacuum forming', 'vacuum formed', 'vacuum form',
    'vacuum forming services',
    'pressure forming', 'pressure formed', 'pressure form',
    'pressure forming services',
    'heavy gauge thermoforming', 'heavy gauge thermoformed',
    'thin gauge thermoforming', 'thin gauge thermoformed',
    
    # Rotomolding - All variations
    'rotomolding', 'rotomolded', 'rotomold', 'roto-molding', 'roto-molded',
    'rotomolding services', 'rotomolding capabilities',
    'rotational molding', 'rotational molded', 'rotationally molded',
    'rotational molding services',
    'roto molding', 'roto molded',
    
    # Compression Molding - All variations
    'compression molding', 'compression molded', 'compression mold',
    'compression molding services', 'compression molding capabilities',
    'smc molding', 'smc molded',
    'bmc molding', 'bmc molded',
    'composite molding', 'composite molded', 'composite mold',
    
    # Additive Manufacturing - All variations
    '3d printing', '3d printed', '3d print', '3d prints', '3-d printing', '3-d printed',
    '3d printing services', '3d printing capabilities',
    'additive manufacturing', 'additive manufactured', 'additively manufactured',
    'additive manufacturing services', 'additive manufacturing capabilities',
    'metal 3d printing', 'metal 3d printed',
    'metal 3d printing services',
    'rapid prototyping', 'rapid prototype', 'rapid prototyped',
    'rapid prototyping services',
    'prototype development', 'prototype', 'prototyped', 'prototyping',
    'fdm', 'sla', 'sls', 'dmls', 'slm',
    'fused deposition modeling', 'fused deposition',
    'stereolithography',
    'selective laser sintering',
]

# Keywords - Expanded with all variations (500+)
KEYWORDS = [
    # CNC & Machining - All variations
    'cnc', 'cnc machining', 'cnc machined', 'cnc machine', 'cnc machines',
    'machining', 'machined', 'machine', 'machines', 'machinist', 'machinists',
    'machine shop', 'machine shops', 'machining shop',
    'mill', 'milled', 'milling', 'mills', 'miller',
    'lathe', 'lathes', 'lathing',
    'turning', 'turned', 'turn', 'turns', 'turner',
    'vmc', 'hmc', 
    '3-axis', '4-axis', '5-axis', '3 axis', '4 axis', '5 axis',
    'multi-axis', 'multi axis', 'multiaxis',
    'swiss-type', 'swiss type', 'swiss',
    'live tooling', 'live tool',
    'cnc lathe', 'cnc lathes',
    'cnc mill', 'cnc mills',
    'precision machining', 'precision machined',
    
    # Laser & Cutting - All variations
    'laser', 'lasers', 'laser cut', 'laser cutting', 'laser-cut',
    'fiber laser', 'fiber lasers', 'fiber laser cut', 'fiber laser cutting',
    'co2 laser', 'co2 lasers', 'co2 laser cut', 'co2 laser cutting',
    'tube laser', 'tube lasers', 'tube laser cut', 'tube laser cutting',
    'laser engraving', 'laser engraved', 'laser engrave',
    'laser marking', 'laser marked', 'laser mark',
    'laser welding', 'laser welded', 'laser weld',
    
    # Waterjet - All variations
    'waterjet', 'water jet', 'water-jet',
    'waterjet cutting', 'waterjet cut', 'water jet cutting', 'water jet cut',
    'abrasive jet', 'abrasive waterjet',
    
    # Press & Forming - All variations
    'press brake', 'press brakes', 'pressbrake',
    'bending', 'bent', 'bend', 'bends', 'bender',
    'metal forming', 'metal formed', 'metal form',
    'forming', 'formed', 'form', 'forms', 'former',
    'brake press', 'brake presses',
    'shearing', 'sheared', 'shear', 'shears',
    'guillotine', 'guillotines',
    'power shear', 'power shears',
    'hydraulic press', 'hydraulic presses',
    
    # Welding - All variations
    'welding', 'welded', 'weld', 'welds', 'welder', 'welders',
    'mig', 'mig welding', 'mig welded', 'mig weld',
    'tig', 'tig welding', 'tig welded', 'tig weld',
    'arc welding', 'arc welded', 'arc weld',
    'spot welding', 'spot welded', 'spot weld',
    'robotic welding', 'robotic welded', 'robotic weld',
    'weld automation', 'automated welding',
    
    # EDM - All variations
    'edm', 'electrical discharge', 'electrical discharge machining',
    'wire edm', 'sinker edm', 'ram edm',
    
    # Grinding - All variations
    'grinding', 'ground', 'grind', 'grinds', 'grinder', 'grinders',
    'surface grinder', 'surface grinding', 'surface ground',
    'cylindrical grinder', 'cylindrical grinding', 'cylindrical ground',
    'od grinding', 'id grinding',
    'centerless grinding', 'centerless ground',
    
    # Sheet Metal & Fabrication - All variations
    'sheet metal', 'sheetmetal',
    'metal fabrication', 'metal fabricated', 'metal fabricate',
    'fabrication', 'fabricated', 'fabricate', 'fabricates', 'fabricator',
    'turret punch', 'turret punching', 'turret punched',
    'punching', 'punched', 'punch',
    'metal stamping', 'metal stamped', 'metal stamp',
    'fab shop', 'fabrication shop',
    
    # Stamping & Die - All variations
    'stamping', 'stamped', 'stamp', 'stamps',
    'progressive die', 'progressive die stamping', 'progressive die stamped',
    'die stamping', 'die stamped',
    'transfer die', 'compound die',
    
    # Casting & Foundry - All variations
    'casting', 'cast', 'casted', 'casts',
    'foundry', 'foundries',
    'die casting', 'die cast', 'diecast', 'die-cast',
    'sand casting', 'sand cast',
    'investment casting', 'investment cast',
    'lost wax', 'lost wax casting',
    'permanent mold', 'permanent mold casting',
    
    # Tooling - All variations
    'tooling', 'tooled', 'tool', 'tools',
    'tool and die', 'tool & die',
    'mold making', 'mold maker', 'moldmaking', 'mould making',
    'die making', 'die maker', 'diemaking',
    'tool design', 'tool designer',
    'jigs and fixtures', 'jigs & fixtures', 'fixtures',
    
    # Plastic Processing - Injection Molding - All variations
    'injection molding', 'injection molded', 'injection mold', 'injection moulding', 'injection moulded',
    'plastic injection', 'plastic molding', 'plastic molded', 'plastic mold',
    'molding', 'molded', 'mold', 'molds', 'moulding', 'moulded', 'moulds',
    'imm', 'injection molding machine',
    'insert molding', 'insert molded', 'insert mold',
    'overmolding', 'overmolded', 'overmold', 'over-molding', 'over-molded',
    'two-shot', 'two shot', '2-shot', '2 shot', '2k',
    'multi-shot', 'multi shot', 'multishot',
    'micro molding', 'micro molded', 'micro mold',
    'thin wall molding', 'thin wall molded',
    
    # Plastic Processing - Extrusion - All variations
    'extrusion', 'extruded', 'extrude', 'extrudes', 'extruder', 'extruders',
    'plastic extrusion', 'plastic extruded',
    'blown film', 'blown film extrusion',
    'profile extrusion', 'profile extruded',
    'pipe extrusion', 'pipe extruded',
    'sheet extrusion', 'sheet extruded',
    'co-extrusion', 'coextrusion', 'co-extruded', 'coextruded',
    
    # Plastic Processing - Blow Molding - All variations
    'blow molding', 'blow molded', 'blow mold', 'blow moulding', 'blow moulded',
    'blow moulding', 'blow-molded', 'blow-molding',
    'bottle', 'bottles', 'container', 'containers',
    'pet blow', 'pet bottles',
    'extrusion blow molding', 'extrusion blow molded',
    'injection blow molding', 'injection blow molded',
    'stretch blow molding', 'stretch blow molded',
    
    # Plastic Processing - Thermoforming - All variations (FIXED!)
    'thermoforming', 'thermoformed', 'thermoform', 'thermoforms',
    'thermo-forming', 'thermo-formed', 'thermo forming', 'thermo formed',
    'vacuum forming', 'vacuum formed', 'vacuum form',
    'vacuum-forming', 'vacuum-formed',
    'pressure forming', 'pressure formed', 'pressure form',
    'pressure-forming', 'pressure-formed',
    'heavy gauge thermoforming', 'heavy gauge thermoformed',
    'thin gauge thermoforming', 'thin gauge thermoformed',
    
    # Plastic Processing - Rotomolding - All variations
    'rotomolding', 'rotomolded', 'rotomold',
    'roto-molding', 'roto-molded', 'roto molding', 'roto molded',
    'rotational molding', 'rotational molded', 'rotationally molded',
    'rotomoulding', 'rotomoulded',
    
    # Plastic Processing - Compression Molding - All variations
    'compression molding', 'compression molded', 'compression mold',
    'compression moulding', 'compression moulded',
    'smc', 'smc molding', 'smc molded', 'sheet molding compound',
    'bmc', 'bmc molding', 'bmc molded', 'bulk molding compound',
    'composite molding', 'composite molded',
    
    # Additive Manufacturing - All variations
    '3d printing', '3d printed', '3d print', '3-d printing', '3-d printed',
    'additive manufacturing', 'additive manufactured', 'additively manufactured',
    'metal 3d printing', 'metal 3d printed',
    'rapid prototyping', 'rapid prototype', 'rapid prototyped',
    'fdm', 'sla', 'sls', 'dmls', 'slm',
    'fused deposition', 'fused deposition modeling',
    'stereolithography',
    
    # Quality & Metrology - All variations
    'cmm', 'coordinate measuring', 'coordinate measurement',
    'inspection', 'inspected', 'inspect', 'inspector',
    'quality control', 'quality assurance', 'qc', 'qa',
    'optical inspection', 'optical inspected',
    'vision system', 'vision inspection',
    'metrology', 'metrological',
    
    # Surface Treatment - All variations
    'anodizing', 'anodized', 'anodize', 'anodization',
    'plating', 'plated', 'plate',
    'powder coating', 'powder coated', 'powder coat',
    'painting', 'painted', 'paint',
    'heat treating', 'heat treated', 'heat treat', 'heat treatment',
    'passivation', 'passivated', 'passivate',
    'electropolishing', 'electropolished', 'electropolish',
    
    # Assembly & Secondary - All variations
    'assembly', 'assembled', 'assemble', 'assembler',
    'kitting', 'kitted', 'kit',
    'packaging', 'packaged', 'package', 'packager',
    'sub-assembly', 'subassembly', 'sub assembly',
    'ultrasonic welding', 'ultrasonic welded',
    'heat staking', 'heat staked',
    'press fit', 'press fitted', 'press-fit',
]

print("✅ Expanded Terms Generated!")
print(f"📊 Equipment Types: {len(EQUIPMENT_TYPES)}")
print(f"📊 Keywords: {len(KEYWORDS)}")
print("\nCopy these lists into main_optimized.py to replace the existing ones!")

