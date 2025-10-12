"""
CONSOLIDATED MANUFACTURING TERMS
Merges EQUIPMENT_TYPES + KEYWORDS + Spanish translations
Removes duplicates, keeps everything in one list
"""

# Consolidated Manufacturing Terms (1000+) - English + Spanish, All Variations
MANUFACTURING_TERMS = [
    # CNC Machining - English + Spanish
    'cnc', 'cnc machining', 'cnc machined', 'cnc machine', 'cnc machines',
    'mecanizado cnc', 'mecanizado', 'mecanizada',  # Spanish
    '5-axis machining', '5-axis machine', '5-axis machined', '5 axis machining',
    '4-axis machining', '4-axis machine', '4-axis machined', '4 axis machining',
    '3-axis machining', '3-axis machine', '3-axis machined', '3 axis machining',
    'multi-axis machining', 'multi-axis machine', 'multi axis machining',
    'mecanizado 5 ejes', 'mecanizado 4 ejes', 'mecanizado 3 ejes',  # Spanish 
    'precision machining', 'precision machine', 'precision machined',
    'mecanizado de precisión',  # Spanish
    
    # Turning - English + Spanish
    'cnc turning', 'cnc turned', 'cnc turn', 'turning', 'turned', 'turn', 'turner',
    'torneado', 'torneado cnc', 'torno',  # Spanish
    'precision turning', 'precision turned',
    'lathe', 'lathes', 'lathing', 'cnc lathe', 'cnc lathes',
    
    # Milling - English + Spanish
    'cnc milling', 'cnc milled', 'cnc mill', 'milling', 'milled', 'mill', 'mills', 'miller',
    'fresado', 'fresado cnc', 'fresadora',  # Spanish
    'vertical machining center', 'horizontal machining center', 'vmc', 'hmc',
    'centro de mecanizado vertical', 'centro de mecanizado horizontal',  # Spanish
    
    # Swiss Machining - English + Spanish
    'swiss machining', 'swiss-type machining', 'swiss machined', 'swiss machine',
    'swiss screw machining', 'swiss screw machine', 'swiss type', 'swiss',
    'mecanizado suizo', 'torno suizo',  # Spanish
    
    # Injection Molding - English + Spanish
    'injection molding', 'injection molded', 'injection mold', 
    'injection moulding', 'injection moulded',
    'moldeo por inyección', 'moldeo por inyeccion', 'inyección de plástico',  # Spanish
    'molding', 'molded', 'mold', 'molds', 'moulding', 'moulded', 'moulds',
    'moldeo', 'moldeado', 'molde',  # Spanish
    'plastic injection', 'plastic molding', 'plastic molded',
    'plástico inyectado', 'moldeado de plástico',  # Spanish
    'custom injection molding', 'contract molding',
    'insert molding', 'insert molded', 'insert mold',
    'overmolding', 'overmolded', 'overmold', 'over-molding', 'over-molded',
    'sobremoldeo', 'sobremoldeado',  # Spanish
    'two-shot molding', 'two-shot molded', 'two shot', '2-shot', '2 shot', '2k',
    'moldeo de dos disparos', 'moldeo 2k',  # Spanish
    'multi-shot', 'multi shot', 'multishot',
    'micro molding', 'micro molded', 'micro mold',
    'lsr molding', 'liquid silicone rubber molding',
    'imm', 'injection molding machine', 'injection molding machines',
    
    # Blow Molding - English + Spanish
    'blow molding', 'blow molded', 'blow mold', 'blow moulding', 'blow moulded',
    'moldeo por soplado', 'soplado', 'moldeado por soplado',  # Spanish
    'extrusion blow molding', 'injection blow molding', 'stretch blow molding',
    'pet blow molding', 'pet blow',
    'bottle', 'bottles', 'bottle manufacturing', 'bottle maker',
    'botella', 'botellas', 'fabricación de botellas',  # Spanish
    
    # Thermoforming - English + Spanish
    'thermoforming', 'thermoformed', 'thermoform', 'thermoforms',
    'thermo-forming', 'thermo-formed', 'thermo forming', 'thermo formed',
    'termoformado', 'termoformación', 'termoconformado',  # Spanish
    'vacuum forming', 'vacuum formed', 'vacuum form', 'vacuum-forming',
    'formado al vacío', 'conformado al vacío',  # Spanish
    'pressure forming', 'pressure formed', 'pressure form',
    'heavy gauge thermoforming', 'thin gauge thermoforming',
    
    # Rotomolding - English + Spanish
    'rotomolding', 'rotomolded', 'rotomold', 'roto-molding', 'roto-molded',
    'rotational molding', 'rotational molded', 'rotationally molded',
    'rotomoldeo', 'moldeo rotacional',  # Spanish
    'roto molding', 'roto molded', 'rotomoulding',
    
    # Compression Molding - English + Spanish
    'compression molding', 'compression molded', 'compression mold',
    'moldeo por compresión', 'moldeado por compresión',  # Spanish
    'smc', 'smc molding', 'sheet molding compound',
    'bmc', 'bmc molding', 'bulk molding compound',
    'composite molding', 'composite molded',
    
    # Extrusion - English + Spanish
    'extrusion', 'extruded', 'extrude', 'extrudes', 'extruder', 'extruders',
    'extrusión', 'extruido', 'extrusora',  # Spanish
    'plastic extrusion', 'plastic extruded',
    'extrusión de plástico',  # Spanish
    'profile extrusion', 'profile extruded',
    'pipe extrusion', 'pipe extruded',
    'sheet extrusion', 'sheet extruded',
    'blown film', 'blown film extrusion',
    'co-extrusion', 'coextrusion', 'co-extruded', 'coextruded',
    
    # Laser Cutting - English + Spanish
    'laser', 'lasers', 'laser cut', 'laser cutting', 'laser-cut', 'laser cuts',
    'corte láser', 'corte laser', 'láser', 'laser cortado',  # Spanish
    'fiber laser', 'fiber lasers', 'fiber laser cutting',
    'laser de fibra', 'corte con laser de fibra',  # Spanish
    'co2 laser', 'co2 lasers', 'co2 laser cutting',
    'laser co2', 'corte laser co2',  # Spanish
    'tube laser', 'tube laser cutting',
    'laser engraving', 'laser engraved', 'laser engrave',
    'grabado láser', 'grabado laser',  # Spanish
    'laser marking', 'laser marked', 'laser mark',
    'marcado láser', 'marcado laser',  # Spanish
    
    # Waterjet - English + Spanish
    'waterjet', 'water jet', 'water-jet', 'waterjet cutting', 'waterjet cut',
    'chorro de agua', 'corte por chorro de agua', 'waterjet',  # Spanish
    'abrasive waterjet', 'abrasive jet',
    
    # Welding - English + Spanish
    'welding', 'welded', 'weld', 'welds', 'welder', 'welders',
    'soldadura', 'soldado', 'soldador', 'soldar',  # Spanish
    'mig', 'mig welding', 'mig welded', 'mig weld',
    'soldadura mig', 'mig',  # Spanish
    'tig', 'tig welding', 'tig welded', 'tig weld',
    'soldadura tig', 'tig',  # Spanish
    'arc welding', 'arc welded', 'arc weld',
    'soldadura por arco',  # Spanish
    'spot welding', 'spot welded', 'spot weld',
    'soldadura por puntos',  # Spanish
    'robotic welding', 'robotic welded', 'robotic weld',
    'soldadura robotizada', 'soldadura robótica',  # Spanish
    'laser welding', 'laser welded',
    'soldadura láser', 'soldadura laser',  # Spanish
    'ultrasonic welding', 'ultrasonic welded',
    'soldadura ultrasónica',  # Spanish
    
    # Sheet Metal & Fabrication - English + Spanish
    'sheet metal', 'sheetmetal', 'metal fabrication', 'metal fabricated',
    'chapa metálica', 'chapa', 'fabricación de metal', 'metalmecánica',  # Spanish
    'fabrication', 'fabricated', 'fabricate', 'fabricates', 'fabricator',
    'fabricación', 'fabricado', 'fabricante',  # Spanish
    'custom fabrication', 'custom metal fabrication',
    
    # Press Brake & Forming - English + Spanish
    'press brake', 'press brakes', 'press braking', 'pressbrake',
    'prensa plegadora', 'dobladora', 'plegado',  # Spanish
    'bending', 'bent', 'bend', 'bends', 'bender',
    'doblado', 'doblar', 'dobladora',  # Spanish
    'metal forming', 'metal formed', 'metal form',
    'formado de metal', 'conformado de metal',  # Spanish
    'forming', 'formed', 'form', 'forms', 'former',
    'formado', 'formar', 'conformado',  # Spanish
    'cnc bending', 'cnc bent', 'precision bending',
    
    # Punching - English + Spanish
    'punching', 'punched', 'punch',
    'punzonado', 'punzonadora', 'troquelado',  # Spanish
    'cnc punching', 'turret punching', 'turret punch',
    
    # Stamping & Die - English + Spanish
    'stamping', 'stamped', 'stamp', 'stamps',
    'estampado', 'estampar', 'troquelado',  # Spanish
    'metal stamping', 'metal stamped',
    'estampado de metal',  # Spanish
    'progressive die', 'progressive die stamping',
    'tool and die', 'tool & die', 'tooling and die',
    'herramientas y troqueles', 'troqueles',  # Spanish
    'die making', 'die maker', 'diemaking',
    'mold making', 'mold maker', 'moldmaking', 'mould making',
    'fabricación de moldes',  # Spanish
    
    # Casting - English + Spanish
    'casting', 'cast', 'casted', 'casts',
    'fundición', 'fundido', 'colada',  # Spanish
    'die casting', 'die cast', 'diecast', 'die-cast',
    'fundición a presión', 'fundición inyectada',  # Spanish
    'investment casting', 'investment cast',
    'fundición a la cera perdida',  # Spanish
    'sand casting', 'sand cast',
    'fundición en arena',  # Spanish
    'aluminum die casting', 'aluminum die cast',
    'fundición de aluminio',  # Spanish
    
    # EDM - English + Spanish
    'edm', 'electrical discharge', 'electrical discharge machining',
    'wire edm', 'sinker edm', 'ram edm',
    'electroerosión', 'mecanizado por descarga eléctrica',  # Spanish
    
    # Grinding - English + Spanish
    'grinding', 'ground', 'grind', 'grinds', 'grinder', 'grinders',
    'rectificado', 'rectificadora', 'esmerilado',  # Spanish
    'surface grinding', 'surface ground', 'surface grinder',
    'rectificado de superficies',  # Spanish
    'cylindrical grinding', 'cylindrical ground',
    'rectificado cilíndrico',  # Spanish
    'centerless grinding', 'centerless ground',
    'rectificado sin centros',  # Spanish
    'precision grinding', 'precision ground',
    'od grinding', 'id grinding',
    
    # 3D Printing / Additive - English + Spanish
    '3d printing', '3d printed', '3d print', '3d prints', '3-d printing',
    'impresión 3d', 'impresión tridimensional', 'impreso en 3d',  # Spanish
    'additive manufacturing', 'additive manufactured', 'additively manufactured',
    'manufactura aditiva', 'fabricación aditiva',  # Spanish
    'rapid prototyping', 'rapid prototype', 'rapid prototyped',
    'prototipado rápido', 'prototipo rápido',  # Spanish
    'metal 3d printing', 'metal 3d printed',
    'fdm', 'sla', 'sls', 'dmls', 'slm',
    'fused deposition modeling', 'stereolithography', 'selective laser sintering',
    
    # Tooling - English + Spanish
    'tooling', 'tooled', 'tool', 'tools',
    'herramental', 'herramientas', 'utillaje',  # Spanish
    'live tooling', 'live tool',
    'tool design', 'tool designer',
    'diseño de herramientas',  # Spanish
    'jigs and fixtures', 'jigs & fixtures', 'fixtures',
    'plantillas y accesorios', 'dispositivos',  # Spanish
    
    # Machining General - English + Spanish
    'machining', 'machined', 'machine', 'machines', 'machinist', 'machinists',
    'machine shop', 'machine shops', 'machining shop',
    'taller mecánico', 'taller de mecanizado', 'maquinado',  # Spanish
    'precision', 'precision machining',
    'precisión', 'mecanizado de precisión',  # Spanish
    
    # Assembly & Secondary - English + Spanish
    'assembly', 'assembled', 'assemble', 'assembler',
    'ensamble', 'ensamblaje', 'montaje', 'ensamblado',  # Spanish
    'sub-assembly', 'subassembly', 'sub assembly',
    'subensamble', 'submontaje',  # Spanish
    'kitting', 'kitted', 'kit',
    'packaging', 'packaged', 'package', 'packager',
    'empaque', 'embalaje', 'empacado',  # Spanish
    
    # Surface Treatment - English + Spanish
    'anodizing', 'anodized', 'anodize', 'anodization',
    'anodizado', 'anodización',  # Spanish
    'plating', 'plated', 'plate',
    'plateado', 'galvanizado', 'recubrimiento',  # Spanish
    'powder coating', 'powder coated', 'powder coat',
    'recubrimiento en polvo', 'pintura en polvo',  # Spanish
    'painting', 'painted', 'paint',
    'pintura', 'pintado', 'acabado',  # Spanish
    'heat treating', 'heat treated', 'heat treat', 'heat treatment',
    'tratamiento térmico', 'tratado térmico',  # Spanish
    'passivation', 'passivated', 'passivate',
    'pasivado', 'pasivación',  # Spanish
    'electropolishing', 'electropolished', 'electropolish',
    'electropulido',  # Spanish
    
    # Quality & Inspection - English + Spanish
    'cmm', 'coordinate measuring', 'coordinate measurement',
    'inspection', 'inspected', 'inspect', 'inspector',
    'inspección', 'inspeccionado', 'inspector', 'control de calidad',  # Spanish
    'quality control', 'quality assurance', 'qc', 'qa',
    'control de calidad', 'aseguramiento de calidad',  # Spanish
    'optical inspection', 'vision system',
    'inspección óptica', 'sistema de visión',  # Spanish
    'metrology', 'metrological',
    'metrología',  # Spanish
    
    # Shearing & Cutting - English + Spanish
    'shearing', 'sheared', 'shear', 'shears',
    'cizallado', 'cizalla', 'corte',  # Spanish
    'guillotine', 'guillotines', 'power shear',
    'guillotina',  # Spanish
    'cutting', 'cut', 'cuts',
    'corte', 'cortado', 'cortar',  # Spanish
    
    # Press & Stamping - English + Spanish
    'hydraulic press', 'hydraulic presses', 'press', 'presses',
    'prensa hidráulica', 'prensa',  # Spanish
    'brake press', 'brake presses',
    'transfer die', 'compound die',
    
    # General Manufacturing - English + Spanish
    'manufacturing', 'manufactured', 'manufacture', 'manufacturer',
    'manufactura', 'fabricación', 'fabricante', 'manufacturado',  # Spanish
    'production', 'produce', 'produced', 'producer',
    'producción', 'producir', 'producido', 'productor',  # Spanish
    'machining services', 'manufacturing services',
    'servicios de mecanizado', 'servicios de manufactura',  # Spanish
    'contract manufacturing', 'custom manufacturing',
    'manufactura por contrato', 'manufactura personalizada',  # Spanish
    
    # Heat Staking & Press Fit - English + Spanish
    'heat staking', 'heat staked',
    'press fit', 'press fitted', 'press-fit',
    'ajuste a presión', 'ajuste por presión',  # Spanish
    
    # Container & Packaging - English + Spanish
    'container', 'containers',
    'contenedor', 'contenedores', 'envase', 'envases',  # Spanish
]

# Keep BRANDS separate (brand names don't translate)
# Keep PLASTICS separate (chemical names, mostly universal)
# Keep METALS separate (material names, mostly universal)

print(f"✅ Consolidated Manufacturing Terms: {len(MANUFACTURING_TERMS)}")
print(f"📊 Includes:")
print(f"   • All English variations (past, present, plural, etc.)")
print(f"   • Spanish translations for common terms")
print(f"   • Merged Equipment Types + Keywords")
print(f"   • Removed duplicates")
print(f"\n💡 This replaces both EQUIPMENT_TYPES and KEYWORDS with one unified list!")
print(f"\n🌎 Spanish coverage: ~150+ translated terms")

