"""
Domain Website Scraper for Manufacturing Keywords
Scrapes domains to find plastics/metalworking equipment keywords, brands, and materials.

Usage:
    python main.py                    # Run once, process all pending domains
    python main.py --continuous       # Run continuously, check for new domains daily
    python main.py --batch-size 100   # Process 100 domains per batch (default: 500)
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import sys
import os
import random
import argparse
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from local.env file
load_dotenv('local.env')

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL_HERE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Table name - your domains table
TABLE_NAME = "domains"

# Rotating User Agents for better scraping success
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Consolidated Manufacturing Terms (650+) - English + Spanish
MANUFACTURING_TERMS = [
    # CNC Machining - English + Spanish
    'cnc', 'cnc machining', 'cnc machined', 'cnc machine', 'cnc machines',
    'mecanizado cnc', 'mecanizado', 'mecanizada',
    '5-axis machining', '5-axis machine', '5-axis machined', '5 axis machining',
    '4-axis machining', '4-axis machine', '4-axis machined', '4 axis machining',
    '3-axis machining', '3-axis machine', '3-axis machined', '3 axis machining',
    'multi-axis machining', 'multi-axis machine', 'multi axis machining',
    'mecanizado 5 ejes', 'mecanizado 4 ejes', 'mecanizado 3 ejes',
    'precision machining', 'precision machine', 'precision machined',
    'mecanizado de precisión',
    
    # Turning - English + Spanish
    'cnc turning', 'cnc turned', 'cnc turn', 'turning', 'turned', 'turn', 'turner',
    'torneado', 'torneado cnc', 'torno',
    'precision turning', 'precision turned',
    'lathe', 'lathes', 'lathing', 'cnc lathe', 'cnc lathes',
    
    # Milling - English + Spanish
    'cnc milling', 'cnc milled', 'cnc mill', 'milling', 'milled', 'mill', 'mills', 'miller',
    'fresado', 'fresado cnc', 'fresadora',
    'vertical machining center', 'horizontal machining center', 'vmc', 'hmc',
    'centro de mecanizado vertical', 'centro de mecanizado horizontal',
    
    # Swiss Machining - English + Spanish
    'swiss machining', 'swiss-type machining', 'swiss machined', 'swiss machine',
    'swiss screw machining', 'swiss screw machine', 'swiss type', 'swiss',
    'mecanizado suizo', 'torno suizo',
    
    # Injection Molding - English + Spanish
    'injection molding', 'injection molded', 'injection mold', 
    'injection moulding', 'injection moulded',
    'moldeo por inyección', 'moldeo por inyeccion', 'inyección de plástico',
    'molding', 'molded', 'mold', 'molds', 'moulding', 'moulded', 'moulds',
    'moldeo', 'moldeado', 'molde',
    'plastic injection', 'plastic molding', 'plastic molded',
    'plástico inyectado', 'moldeado de plástico',
    'custom injection molding', 'contract molding',
    'insert molding', 'insert molded', 'insert mold',
    'overmolding', 'overmolded', 'overmold', 'over-molding', 'over-molded',
    'sobremoldeo', 'sobremoldeado',
    'two-shot molding', 'two-shot molded', 'two shot', '2-shot', '2 shot', '2k',
    'moldeo de dos disparos', 'moldeo 2k',
    'multi-shot', 'multi shot', 'multishot',
    'micro molding', 'micro molded', 'micro mold',
    'lsr molding', 'liquid silicone rubber molding',
    'imm', 'injection molding machine', 'injection molding machines',
    
    # Blow Molding - English + Spanish
    'blow molding', 'blow molded', 'blow mold', 'blow moulding', 'blow moulded',
    'moldeo por soplado', 'soplado', 'moldeado por soplado',
    'extrusion blow molding', 'injection blow molding', 'stretch blow molding',
    'pet blow molding', 'pet blow',
    'bottle', 'bottles', 'bottle manufacturing', 'bottle maker',
    'botella', 'botellas', 'fabricación de botellas',
    
    # Thermoforming - English + Spanish
    'thermoforming', 'thermoformed', 'thermoform', 'thermoforms',
    'thermo-forming', 'thermo-formed', 'thermo forming', 'thermo formed',
    'termoformado', 'termoformación', 'termoconformado',
    'vacuum forming', 'vacuum formed', 'vacuum form', 'vacuum-forming',
    'formado al vacío', 'conformado al vacío',
    'pressure forming', 'pressure formed', 'pressure form',
    'heavy gauge thermoforming', 'thin gauge thermoforming',
    
    # Rotomolding - English + Spanish
    'rotomolding', 'rotomolded', 'rotomold', 'roto-molding', 'roto-molded',
    'rotational molding', 'rotational molded', 'rotationally molded',
    'rotomoldeo', 'moldeo rotacional',
    'roto molding', 'roto molded', 'rotomoulding',
    
    # Compression Molding - English + Spanish
    'compression molding', 'compression molded', 'compression mold',
    'moldeo por compresión', 'moldeado por compresión',
    'smc', 'smc molding', 'sheet molding compound',
    'bmc', 'bmc molding', 'bulk molding compound',
    'composite molding', 'composite molded',
    
    # Extrusion - English + Spanish
    'extrusion', 'extruded', 'extrude', 'extrudes', 'extruder', 'extruders',
    'extrusión', 'extruido', 'extrusora',
    'plastic extrusion', 'plastic extruded',
    'extrusión de plástico',
    'profile extrusion', 'profile extruded',
    'pipe extrusion', 'pipe extruded',
    'sheet extrusion', 'sheet extruded',
    'blown film', 'blown film extrusion',
    'co-extrusion', 'coextrusion', 'co-extruded', 'coextruded',
    
    # Laser Cutting - English + Spanish
    'laser', 'lasers', 'laser cut', 'laser cutting', 'laser-cut', 'laser cuts',
    'corte láser', 'corte laser', 'láser', 'laser cortado',
    'fiber laser', 'fiber lasers', 'fiber laser cutting',
    'laser de fibra', 'corte con laser de fibra',
    'co2 laser', 'co2 lasers', 'co2 laser cutting',
    'laser co2', 'corte laser co2',
    'tube laser', 'tube laser cutting',
    'laser engraving', 'laser engraved', 'laser engrave',
    'grabado láser', 'grabado laser',
    'laser marking', 'laser marked', 'laser mark',
    'marcado láser', 'marcado laser',
    
    # Waterjet - English + Spanish
    'waterjet', 'water jet', 'water-jet', 'waterjet cutting', 'waterjet cut',
    'chorro de agua', 'corte por chorro de agua',
    'abrasive waterjet', 'abrasive jet',
    
    # Welding - English + Spanish
    'welding', 'welded', 'weld', 'welds', 'welder', 'welders',
    'soldadura', 'soldado', 'soldador', 'soldar',
    'mig', 'mig welding', 'mig welded', 'mig weld',
    'soldadura mig',
    'tig', 'tig welding', 'tig welded', 'tig weld',
    'soldadura tig',
    'arc welding', 'arc welded', 'arc weld',
    'soldadura por arco',
    'spot welding', 'spot welded', 'spot weld',
    'soldadura por puntos',
    'robotic welding', 'robotic welded', 'robotic weld',
    'soldadura robotizada', 'soldadura robótica',
    'laser welding', 'laser welded',
    'soldadura láser', 'soldadura laser',
    'ultrasonic welding', 'ultrasonic welded',
    'soldadura ultrasónica',
    
    # Sheet Metal & Fabrication - English + Spanish
    'sheet metal', 'sheetmetal', 'metal fabrication', 'metal fabricated',
    'chapa metálica', 'chapa', 'fabricación de metal', 'metalmecánica',
    'fabrication', 'fabricated', 'fabricate', 'fabricates', 'fabricator',
    'fabricación', 'fabricado', 'fabricante',
    'custom fabrication', 'custom metal fabrication',
    
    # Press Brake & Forming - English + Spanish
    'press brake', 'press brakes', 'press braking', 'pressbrake',
    'prensa plegadora', 'dobladora', 'plegado',
    'bending', 'bent', 'bend', 'bends', 'bender',
    'doblado', 'doblar', 'dobladora',
    'metal forming', 'metal formed', 'metal form',
    'formado de metal', 'conformado de metal',
    'forming', 'formed', 'form', 'forms', 'former',
    'formado', 'formar', 'conformado',
    'cnc bending', 'cnc bent', 'precision bending',
    
    # Punching - English + Spanish
    'punching', 'punched', 'punch',
    'punzonado', 'punzonadora', 'troquelado',
    'cnc punching', 'turret punching', 'turret punch',
    
    # Stamping & Die - English + Spanish
    'stamping', 'stamped', 'stamp', 'stamps',
    'estampado', 'estampar', 'troquelado',
    'metal stamping', 'metal stamped',
    'estampado de metal',
    'progressive die', 'progressive die stamping',
    'tool and die', 'tool & die', 'tooling and die',
    'herramientas y troqueles', 'troqueles',
    'die making', 'die maker', 'diemaking',
    'mold making', 'mold maker', 'moldmaking', 'mould making',
    'fabricación de moldes',
    
    # Casting - English + Spanish
    'casting', 'cast', 'casted', 'casts',
    'fundición', 'fundido', 'colada',
    'die casting', 'die cast', 'diecast', 'die-cast',
    'fundición a presión', 'fundición inyectada',
    'investment casting', 'investment cast',
    'fundición a la cera perdida',
    'sand casting', 'sand cast',
    'fundición en arena',
    'aluminum die casting', 'aluminum die cast',
    'fundición de aluminio',
    
    # EDM - English + Spanish
    'edm', 'electrical discharge', 'electrical discharge machining',
    'wire edm', 'sinker edm', 'ram edm',
    'electroerosión', 'mecanizado por descarga eléctrica',
    
    # Grinding - English + Spanish
    'grinding', 'ground', 'grind', 'grinds', 'grinder', 'grinders',
    'rectificado', 'rectificadora', 'esmerilado',
    'surface grinding', 'surface ground', 'surface grinder',
    'rectificado de superficies',
    'cylindrical grinding', 'cylindrical ground',
    'rectificado cilíndrico',
    'centerless grinding', 'centerless ground',
    'rectificado sin centros',
    'precision grinding', 'precision ground',
    'od grinding', 'id grinding',
    
    # 3D Printing / Additive - English + Spanish
    '3d printing', '3d printed', '3d print', '3d prints', '3-d printing',
    'impresión 3d', 'impresión tridimensional', 'impreso en 3d',
    'additive manufacturing', 'additive manufactured', 'additively manufactured',
    'manufactura aditiva', 'fabricación aditiva',
    'rapid prototyping', 'rapid prototype', 'rapid prototyped',
    'prototipado rápido', 'prototipo rápido',
    'metal 3d printing', 'metal 3d printed',
    'fdm', 'sla', 'sls', 'dmls', 'slm',
    'fused deposition modeling', 'stereolithography', 'selective laser sintering',
    
    # Tooling - English + Spanish
    'tooling', 'tooled', 'tool', 'tools',
    'herramental', 'herramientas', 'utillaje',
    'live tooling', 'live tool',
    'tool design', 'tool designer',
    'diseño de herramientas',
    'jigs and fixtures', 'jigs & fixtures', 'fixtures',
    'plantillas y accesorios', 'dispositivos',
    
    # Machining General - English + Spanish
    'machining', 'machined', 'machine', 'machines', 'machinist', 'machinists',
    'machine shop', 'machine shops', 'machining shop',
    'taller mecánico', 'taller de mecanizado', 'maquinado',
    'precision', 'precision machining',
    'precisión', 'mecanizado de precisión',
    
    # Assembly & Secondary - English + Spanish
    'assembly', 'assembled', 'assemble', 'assembler',
    'ensamble', 'ensamblaje', 'montaje', 'ensamblado',
    'sub-assembly', 'subassembly', 'sub assembly',
    'subensamble', 'submontaje',
    'kitting', 'kitted', 'kit',
    'packaging', 'packaged', 'package', 'packager',
    'empaque', 'embalaje', 'empacado',
    
    # Surface Treatment - English + Spanish
    'anodizing', 'anodized', 'anodize', 'anodization',
    'anodizado', 'anodización',
    'plating', 'plated', 'plate',
    'plateado', 'galvanizado', 'recubrimiento',
    'powder coating', 'powder coated', 'powder coat',
    'recubrimiento en polvo', 'pintura en polvo',
    'painting', 'painted', 'paint',
    'pintura', 'pintado', 'acabado',
    'heat treating', 'heat treated', 'heat treat', 'heat treatment',
    'tratamiento térmico', 'tratado térmico',
    'passivation', 'passivated', 'passivate',
    'pasivado', 'pasivación',
    'electropolishing', 'electropolished', 'electropolish',
    'electropulido',
    
    # Quality & Inspection - English + Spanish
    'cmm', 'coordinate measuring', 'coordinate measurement',
    'inspection', 'inspected', 'inspect', 'inspector',
    'inspección', 'inspeccionado', 'inspector', 'control de calidad',
    'quality control', 'quality assurance', 'qc', 'qa',
    'control de calidad', 'aseguramiento de calidad',
    'optical inspection', 'vision system',
    'inspección óptica', 'sistema de visión',
    'metrology', 'metrological',
    'metrología',
    
    # Shearing & Cutting - English + Spanish
    'shearing', 'sheared', 'shear', 'shears',
    'cizallado', 'cizalla', 'corte',
    'guillotine', 'guillotines', 'power shear',
    'guillotina',
    'cutting', 'cut', 'cuts',
    'corte', 'cortado', 'cortar',
    
    # Press & Stamping - English + Spanish
    'hydraulic press', 'hydraulic presses', 'press', 'presses',
    'prensa hidráulica', 'prensa',
    'brake press', 'brake presses',
    'transfer die', 'compound die',
    
    # General Manufacturing - English + Spanish
    'manufacturing', 'manufactured', 'manufacture', 'manufacturer',
    'manufactura', 'fabricación', 'fabricante', 'manufacturado',
    'production', 'produce', 'produced', 'producer',
    'producción', 'producir', 'producido', 'productor',
    'machining services', 'manufacturing services',
    'servicios de mecanizado', 'servicios de manufactura',
    'contract manufacturing', 'custom manufacturing',
    'manufactura por contrato', 'manufactura personalizada',
    
    # Heat Staking & Press Fit - English + Spanish
    'heat staking', 'heat staked',
    'press fit', 'press fitted', 'press-fit',
    'ajuste a presión', 'ajuste por presión',
    
    # Container & Packaging - English + Spanish
    'container', 'containers',
    'contenedor', 'contenedores', 'envase', 'envases',
]

# Equipment brands (300+)
BRANDS = [
    # CNC Machine Tools & Machining Centers
    'haas', 'haas automation', 'mazak', 'yamazaki mazak', 'dmg mori', 'mori seiki', 
    'okuma', 'makino', 'fanuc', 'brother', 'nakamura', 'nakamura-tome', 'matsuura', 
    'kitamura', 'toyoda', 'jtekt', 'tsugami', 'star micronics', 'citizen machinery', 
    'miyano', 'takisawa', 'wasino', 'forest line', 'enshu', 'johnford', 'femco',
    'hardinge', 'fadal', 'hurco', 'tree', 'bridgeport', 'mag', 'methods machine', 
    'milltronics', 'tormach', 'sharp', 'dmg', 'gildemeister', 'maho', 'deckel', 
    'hermle', 'chiron', 'spinner', 'emag', 'grob', 'starrag', 'studer', 'kellenberger', 
    'schaublin', 'mikron', 'willemin-macodel', 'reiden', 'fehlmann', 'fidia', 'anayak',
    'doosan', 'hyundai wia', 'kia', 'smec', 'hwacheon', 'yama seiki', 'daewoo',
    'dmtg', 'shenyang', 'dalian', 'qinchuan', 'cncpros', 'gf machining', 'kern',
    
    # Laser Cutting Systems
    'trumpf', 'amada', 'bystronic', 'mazak optonics', 'prima power', 'mitsubishi',
    'mitsubishi electric', 'lvd', 'salvagnini', 'han\'s laser', 'hans laser', 
    'huagong tech', 'bodor', 'hymson', 'hsg laser', 'penta laser', 'yawei', 
    'senfeng', 'raycus', 'max photonics', 'jpt', 'coherent', 'ipg photonics', 
    'rofin', 'trumpf laser', 'bystronic laser',
    
    # Waterjet Cutting
    'omax', 'jet edge', 'wardjet', 'waterjet corporation', 'techni waterjet', 
    'kmt', 'hypertherm', 'esab', 'koike aronson', 'accustream', 'dardi', 
    'waterjet sweden', 'resato',
    
    # Press Brakes & Bending
    'accurpress', 'ermaksan', 'durma', 'safan darley', 'wysong', 'gasparini', 
    'haco', 'baykal', 'dener', 'colgar', 'warcom', 'accurl', 'baileigh',
    'cincinnati', 'jmt usa', 'harsle', 'toyokoki', 'adh machine',
    'wilson tool', 'wila', 'mate precision', 'promecam', 'trumpf tools',
    
    # Welding Equipment
    'miller', 'miller electric', 'lincoln electric', 'lincoln', 'hobart',
    'fronius', 'kemppi', 'kjellberg',
    
    # Robotics & Automation
    'panasonic', 'yaskawa', 'motoman', 'fanuc robotics', 'abb robotics', 'kuka',
    'abb', 'otc daihen', 'cloos', 'igm robotics', 'kawasaki',
    
    # EDM
    'sodick', 'charmilles', 'agie', 'agie charmilles', 'mc machinery', 
    'japax', 'ona', 'accutex', 'chmer',
    
    # Grinding Machines
    'chevalier', 'kent', 'mitsui', 'jones & shipman', 'boyar schultz', 
    'walter', 'anca', 'brown & sharpe', 'junker', 'kapp', 'agathon',
    
    # Stamping & Presses
    'aida', 'komatsu', 'schuler', 'bruderer', 'minster', 'danly', 'verson',
    'clearing', 'niagara', 'bliss', 'arisa', 'chin fong', 'seyi',
    
    # Casting & Foundry
    'inductotherm', 'disa', 'loramendi', 'italpresse', 'buhler', 'idra', 'ube', 'frech',
    
    # Injection Molding Machines
    'engel', 'arburg', 'haitian', 'haitian international', 'sumitomo', 
    'sumitomo demag', 'nissei', 'nissei plastic', 'husky', 'wittmann battenfeld', 
    'battenfeld', 'boy', 'boy machines', 'milacron', 'toshiba machine', 
    'shibaura machine', 'chen hsong', 'krauss maffei', 'kraussmaffei', 
    'fanuc roboshot', 'jsw', 'japan steel works', 'negri bossi', 'fu chun shin', 
    'dakumar', 'yizumi', 'tederic', 'bole machinery', 'zhafir', 
    'demag', 'ferromatik', 'van dorn', 'netstal', 'sandretto',
    
    # Extrusion Equipment
    'davis-standard', 'davis standard', 'cincinnati milacron',
    'graham engineering', 'battenfeld-cincinnati', 'battenfeld cincinnati', 
    'leistritz', 'coperion', 'berstorff', 'reifenhauser', 'windmoller',
    'bandera', 'starlinger', 'bausano', 'entek', 'amut', 'erema',
    
    # Blow Molding Machines
    'kautex', 'bekum', 'bekum america', 'uniloy', 'wilmington', 'magic', 
    'jomar', 'techne', 'graham', 'plastiblow', 'sidel', 'khs', 'sipa',
    'aoki', 'nissei asb',
    
    # Thermoforming Machines
    'brown machine', 'illig', 'gabler', 'geiss', 'multivac', 'kiefel',
    'gn thermoforming', 'sencorp', 'maac machinery',
    
    # 3D Printing & Additive Manufacturing
    'stratasys', '3d systems', 'hp', 'eos', 'formlabs', 'ultimaker', 'markforged',
    'carbon', 'prusa', 'desktop metal', 'velo3d', 'slm solutions', 'renishaw',
    'ge additive',
    
    # Auxiliary Equipment
    'conair', 'novatec', 'motan', 'maguire', 'matsui', 'piovan', 'wittmann',
    'sterling', 'dri-air', 'thermal care', 'aec',
]

# Plastics (200+)
PLASTICS = [
    # Commodity Plastics
    'pet', 'pete', 'polyethylene terephthalate',
    'hdpe', 'high-density polyethylene', 'high density polyethylene',
    'ldpe', 'low-density polyethylene', 'low density polyethylene',
    'lldpe', 'linear low-density polyethylene',
    'pp', 'polypropylene', 'homopolymer pp', 'copolymer pp',
    'ps', 'polystyrene', 'hips', 'high impact polystyrene',
    'pvc', 'polyvinyl chloride', 'rigid pvc', 'flexible pvc',
    'eva', 'ethylene vinyl acetate',
    
    # Engineering Plastics
    'abs', 'acrylonitrile butadiene styrene',
    'pa', 'nylon', 'polyamide', 'pa6', 'pa66', 'pa6/6', 'pa11', 'pa12',
    'nylon 6', 'nylon 66', 'nylon 6/6', 'nylon 11', 'nylon 12',
    'pc', 'polycarbonate', 'lexan', 'makrolon',
    'pom', 'acetal', 'delrin', 'polyoxymethylene',
    'pbt', 'polybutylene terephthalate',
    'petg', 'pet-g', 'glycol-modified pet',
    'san', 'styrene acrylonitrile',
    'asa', 'acrylonitrile styrene acrylate',
    'pmma', 'acrylic', 'plexiglass',
    'pc/abs', 'pc abs blend',
    
    # High Performance Plastics
    'peek', 'polyetheretherketone',
    'pei', 'ultem', 'polyetherimide',
    'psu', 'polysulfone',
    'pes', 'polyethersulfone',
    'ppsu', 'polyphenylsulfone',
    'pps', 'polyphenylene sulfide', 'ryton',
    'pai', 'polyamide-imide', 'torlon',
    'lcp', 'liquid crystal polymer',
    'pvdf', 'polyvinylidene fluoride', 'kynar',
    'ptfe', 'teflon', 'polytetrafluoroethylene',
    'pfa', 'perfluoroalkoxy',
    'fep', 'fluorinated ethylene propylene',
    
    # Thermoplastic Elastomers
    'tpe', 'thermoplastic elastomer',
    'tpu', 'thermoplastic polyurethane',
    'tpo', 'thermoplastic olefin',
    'tpv', 'thermoplastic vulcanizate',
    'sebs', 'styrene ethylene butylene styrene',
    'sbs', 'styrene butadiene styrene',
    
    # Silicones
    'lsr', 'liquid silicone rubber',
    'hcr', 'high consistency rubber',
    
    # Recycled & Sustainable
    'rpet', 'r-pet', 'recycled pet',
    'pcr', 'post-consumer recycled',
    'pir', 'post-industrial recycled',
    'recycled plastic', 'recycled resin', 'regrind',
    'pla', 'polylactic acid',
    
    # General Terms
    'resin', 'pellets', 'polymer', 'thermoplastic', 'thermoset',
    'glass-filled', 'glass filled', 'fiber-reinforced', 'fiber reinforced',
    'carbon fiber reinforced', 'mineral filled',
    'flame retardant', 'uv stabilized', 'food grade', 'medical grade',
]

# Metals (200+)
METALS = [
    # Aluminum Alloys
    'aluminum', 'aluminium', 'aluminum alloy',
    '6061', '6061-t6', '6061 aluminum',
    '6063', '6063-t5', '6063 aluminum',
    '7075', '7075-t6', '7075 aluminum',
    '5052', '5052 aluminum', '5083', '5083 aluminum',
    '2024', '2024-t3', '2024 aluminum',
    '3003', '3003 aluminum',
    'cast aluminum', 'a356', 'a380',
    
    # Carbon & Alloy Steel
    'carbon steel', 'mild steel', 'low carbon steel',
    'alloy steel', 'tool steel', 'spring steel',
    '4140', '4140 steel', '4340', '4340 steel',
    '1018', '1018 steel', '1045', '1045 steel',
    'a36', 'a36 steel',
    '1020', '1020 steel', '12l14', '12l14 steel',
    '8620', '8620 steel', '4130', '4130 steel',
    'a2 tool steel', 'd2 tool steel', 'o1 tool steel',
    
    # Stainless Steel
    'stainless steel', 'stainless', '304 stainless', '316 stainless',
    '303 stainless', '17-4 stainless', '17-4 ph',
    '304l', '304l stainless', '316l', '316l stainless',
    '321 stainless', '410 stainless', '420 stainless',
    '430 stainless', '440c stainless',
    'duplex stainless', 'super duplex',
    
    # Brass & Bronze
    'brass', 'brass alloy', 'c360', 'free-cutting brass',
    'bronze', 'phosphor bronze', 'aluminum bronze', 'silicon bronze',
    'copper alloy', 'copper', 'c110', 'ofhc copper',
    'beryllium copper', 'c172',
    
    # Titanium
    'titanium', 'titanium alloy', 'ti-6al-4v', 'ti6al4v', 
    'grade 5 titanium', 'grade 2 titanium',
    'cp titanium',
    
    # Nickel Alloys & Superalloys
    'inconel', 'inconel 625', 'inconel 718', 'inconel 600',
    'hastelloy', 'hastelloy c-276', 'hastelloy x',
    'monel', 'monel 400', 'monel k-500',
    'incoloy', 'incoloy 800',
    'nickel alloy', 'nickel', 'nickel 200',
    'waspaloy', 'superalloy',
    
    # Other Metals
    'magnesium', 'magnesium alloy', 'az31',
    'zinc', 'zinc alloy', 'zamak',
    
    # General Metal Terms
    'heat-treated', 'cold-rolled', 'hot-rolled',
    'hardened steel', 'annealed',
    'galvanized steel', 'zinc plated',
    'sheet metal', 'plate metal', 'bar stock',
    'round bar', 'square bar', 'hex bar',
    'structural steel', 'tube', 'pipe',
]


# Circuit Breaker Constants
MAX_DOMAIN_TIME = 60  # 60 seconds max per domain
MAX_CONSECUTIVE_FAILURES = 3
MAX_PAGES_PER_DOMAIN = 15

# Performance tracking
performance_stats = {
    'start_time': None,
    'domains_processed': 0,
    'successes': 0,
    'failures': 0,
    'no_keywords': 0,
    'batch_times': [],
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    sys.stdout.flush()

def is_obviously_invalid_domain(domain: str) -> bool:
    """Quick check for obviously invalid domains"""
    if not domain or not domain.strip():
        return True
    
    domain = domain.strip().lower()
    
    if domain in ['#na', 'n/a', 'na', '', 'none', 'null']:
        return True
    
    if 'google.comsearch' in domain or 'search?' in domain:
        return True
    
    if '.' not in domain:
        return True
    
    return False

def extract_internal_links(html, base_domain):
    """Extract internal links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        
        if href.startswith('/'):
            url = f'https://{base_domain}{href}'
        elif href.startswith('http'):
            url = href
        else:
            continue
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            link_domain = parsed.netloc.replace('www.', '')
            
            if link_domain == base_domain.replace('www.', ''):
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                links.append(clean_url)
        except:
            continue
    
    return list(set(links))[:MAX_PAGES_PER_DOMAIN]

def detect_manufacturing(html, url):
    """Detect manufacturing capabilities from page content"""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text().lower()
    combined = text + ' ' + url.lower()
    
    found = {
        'keywords': set(),
        'brands': set(),
        'plastics': set(),
        'metals': set()
    }
    
    # Search manufacturing terms
    for term in MANUFACTURING_TERMS:
        if term in combined:
            found['keywords'].add(term)
    
    # Search brands (with word boundaries)
    for brand in BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    # Search plastics (with word boundaries)
    for p in PLASTICS:
        if re.search(r'\b' + re.escape(p) + r'\b', combined, re.IGNORECASE):
            found['plastics'].add(p)
    
    # Search metals (with word boundaries)
    for m in METALS:
        if re.search(r'\b' + re.escape(m) + r'\b', combined, re.IGNORECASE):
            found['metals'].add(m)
    
    return found

async def scrape_page(url, session, retry=0):
    """Scrape a single page"""
    try:
        timeout = 15.0 if retry == 0 else 30.0
        
        response = await session.get(
            url, 
            timeout=timeout,
            follow_redirects=True
        )
        
        if response.status_code == 429:
            log(f"    ⏳ Rate limited, waiting 5s...")
            await asyncio.sleep(5)
            if retry < 2:
                return await scrape_page(url, session, retry + 1)
            return None
        elif response.status_code in [502, 503, 504]:
            await asyncio.sleep(3)
            if retry < 1:
                return await scrape_page(url, session, retry + 1)
            return None
        elif response.status_code >= 400:
            if retry < 1:
                await asyncio.sleep(1)
                return await scrape_page(url, session, retry + 1)
            return None
            
        html = response.text
        indicators = detect_manufacturing(html, url)
        
        return {
            'url': url,
            'html': html,
            'indicators': indicators
        }
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError):
        if retry < 1:
            await asyncio.sleep(1)
            return await scrape_page(url, session, retry + 1)
        return None
    except Exception:
        return None

async def try_url_variations(domain, session):
    """Try multiple URL variations to reach the domain"""
    clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    
    url_variations = [
        f'https://{clean_domain}',
        f'https://www.{clean_domain}',
        f'http://{clean_domain}',
        f'http://www.{clean_domain}',
    ]
    
    for attempt in range(2):
        for url in url_variations:
            try:
                result = await scrape_page(url, session)
                if result:
                    log(f"  ✅ Connected via: {url}")
                    return result, url
            except:
                continue
        
        if attempt == 0:
            await asyncio.sleep(2)
    
    return None, None

async def crawl_domain(base_url, session):
    """Crawl a domain and extract manufacturing keywords"""
    clean_domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    domain = clean_domain
    
    domain_start_time = datetime.now()
    consecutive_failures = 0
    
    log(f"🔍 Crawling {domain}")
    
    # Human-like delay
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Check for obviously invalid domain
    if is_obviously_invalid_domain(domain):
        log(f"  ❌ Invalid domain format - skipping")
        performance_stats['failures'] += 1
        
        try:
            supabase.table(TABLE_NAME).update({
                'website_scrape_status': 'error',
                'website_scraped_at': datetime.now().isoformat()
            }).eq('domain', domain).execute()
        except Exception as e:
            log(f"  ⚠️ Failed to save error status: {str(e)}")
        return None
    
    # Try to scrape homepage
    homepage, successful_url = await try_url_variations(domain, session)
    
    if not homepage:
        log(f"  ❌ All URL variations failed - domain unreachable")
        performance_stats['failures'] += 1
        
        try:
            supabase.table(TABLE_NAME).update({
                'website_scrape_status': 'timeout',
                'website_scraped_at': datetime.now().isoformat()
            }).eq('domain', domain).execute()
        except Exception as e:
            log(f"  ⚠️ Failed to save timeout status: {str(e)}")
        return None
    
    log(f"  ✅ Homepage loaded successfully")
    
    # Extract and crawl internal links
    internal_links = extract_internal_links(homepage['html'], domain)
    log(f"  📄 Found {len(internal_links)} internal pages to crawl")
    
    all_pages = [homepage]
    
    for page_url in internal_links:
        elapsed = (datetime.now() - domain_start_time).total_seconds()
        if elapsed > MAX_DOMAIN_TIME:
            log(f"  ⏱️ Domain timeout - stopping with {len(all_pages)} pages")
            break
        
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            log(f"  ⚠️ Too many failures - stopping with {len(all_pages)} pages")
            break
        
        try:
            page_result = await scrape_page(page_url, session)
            if page_result:
                all_pages.append(page_result)
                consecutive_failures = 0
            else:
                consecutive_failures += 1
        except:
            consecutive_failures += 1
    
    # Aggregate results
    all_keywords = set()
    all_brands = set()
    all_plastics = set()
    all_metals = set()
    
    for page in all_pages:
        if page:
            all_keywords.update(page['indicators']['keywords'])
            all_brands.update(page['indicators']['brands'])
            all_plastics.update(page['indicators']['plastics'])
            all_metals.update(page['indicators']['metals'])
    
    total_matches = len(all_keywords) + len(all_brands) + len(all_plastics) + len(all_metals)
    
    log(f"  ✅ {total_matches} total matches | {len(all_pages)} pages crawled")
    
    # Determine status
    if total_matches > 0:
        status = 'completed'
        performance_stats['successes'] += 1
    else:
        status = 'no_keywords'
        performance_stats['no_keywords'] += 1
    
    # Prepare result for database
    result = {
        'website_keywords': list(all_keywords) if all_keywords else None,
        'website_brands': list(all_brands) if all_brands else None,
        'website_plastics': list(all_plastics) if all_plastics else None,
        'website_metals': list(all_metals) if all_metals else None,
        'website_scrape_status': status,
        'website_scraped_at': datetime.now().isoformat()
    }
    
    # Save to Supabase
    try:
        supabase.table(TABLE_NAME).update(result).eq('domain', domain).execute()
        log(f"  💾 Saved to Supabase ({status})")
    except Exception as e:
        log(f"  ❌ Failed to save: {str(e)}")
        performance_stats['failures'] += 1
    
    return result

async def process_batch(domains, batch_size=500):
    """Process a batch of domains"""
    log(f"🏭 Starting batch of {len(domains)} domains...\n")
    
    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        },
        timeout=httpx.Timeout(45.0, connect=15.0),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0
        )
    ) as session:
        
        semaphore = asyncio.Semaphore(50)  # 50 concurrent domains
        
        async def crawl_with_limit(domain):
            async with semaphore:
                await crawl_domain(f'https://{domain}', session)
                performance_stats['domains_processed'] += 1
        
        tasks = [crawl_with_limit(domain) for domain in domains]
        await asyncio.gather(*tasks)

def get_pending_domains(limit=500):
    """Fetch domains that need scraping"""
    try:
        # Get domains where website_scrape_status is 'pending' or NULL
        response = supabase.table(TABLE_NAME).select('domain').or_(
            'website_scrape_status.eq.pending,website_scrape_status.is.null'
        ).limit(limit).execute()
        
        domains = [row['domain'] for row in response.data if row.get('domain')]
        
        # Clean and deduplicate
        cleaned = []
        seen = set()
        for d in domains:
            if not d or not d.strip():
                continue
            clean = d.strip().lower()
            clean = clean.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            if clean not in seen:
                seen.add(clean)
                cleaned.append(clean)
        
        return cleaned
    except Exception as e:
        log(f"❌ Error fetching domains: {str(e)}")
        return []

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Domain Website Scraper for Manufacturing Keywords')
    parser.add_argument('--continuous', action='store_true', help='Run continuously, checking for new domains daily')
    parser.add_argument('--batch-size', type=int, default=500, help='Number of domains per batch (default: 500)')
    parser.add_argument('--check-interval', type=int, default=24, help='Hours between checks in continuous mode (default: 24)')
    args = parser.parse_args()
    
    log("🚀 DOMAIN WEBSITE SCRAPER v1.0")
    log(f"📅 Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"🗄️  Table: {TABLE_NAME}")
    log(f"📦 Batch size: {args.batch_size}")
    log(f"🔄 Mode: {'Continuous' if args.continuous else 'Single run'}")
    log("")
    
    performance_stats['start_time'] = datetime.now()
    
    while True:
        batch_num = 1
        
        while True:
            batch_start = datetime.now()
            
            log(f"\n{'='*60}")
            log(f"📦 BATCH {batch_num}")
            log(f"{'='*60}\n")
            
            # Fetch pending domains
            log("📡 Fetching pending domains from Supabase...")
            domains = get_pending_domains(args.batch_size)
            
            if not domains:
                log("\n🎉 ALL DOMAINS PROCESSED!")
                break
            
            log(f"📊 Found {len(domains)} domains to process\n")
            
            # Process batch
            await process_batch(domains, args.batch_size)
            
            # Batch stats
            batch_time = (datetime.now() - batch_start).total_seconds()
            performance_stats['batch_times'].append(batch_time)
            
            domains_per_min = (len(domains) / batch_time) * 60 if batch_time > 0 else 0
            
            log(f"\n{'='*60}")
            log(f"✅ BATCH {batch_num} COMPLETE!")
            log(f"{'='*60}")
            log(f"⏱️  Batch time: {batch_time:.1f}s")
            log(f"🚀 Speed: {domains_per_min:.1f} domains/minute")
            log(f"📊 Processed: {performance_stats['domains_processed']} total")
            log(f"✅ With keywords: {performance_stats['successes']}")
            log(f"📭 No keywords: {performance_stats['no_keywords']}")
            log(f"❌ Failures: {performance_stats['failures']}")
            
            batch_num += 1
            
            # Cooldown between batches
            log(f"\n⏸️  Cooldown: 5 seconds before next batch...")
            await asyncio.sleep(5)
        
        # If not continuous mode, exit after processing all domains
        if not args.continuous:
            break
        
        # In continuous mode, wait and check again
        log(f"\n💤 Waiting {args.check_interval} hours before checking for new domains...")
        await asyncio.sleep(args.check_interval * 3600)
        log(f"\n🔄 Checking for new domains...")
    
    # Final summary
    total_time = (datetime.now() - performance_stats['start_time']).total_seconds()
    log(f"\n{'='*60}")
    log(f"🎉 SCRAPING COMPLETE!")
    log(f"{'='*60}")
    log(f"⏱️  Total time: {total_time/60:.1f} minutes")
    log(f"📊 Total domains: {performance_stats['domains_processed']}")
    log(f"✅ With keywords: {performance_stats['successes']}")
    log(f"📭 No keywords: {performance_stats['no_keywords']}")
    log(f"❌ Failures: {performance_stats['failures']}")
    if total_time > 0:
        log(f"🚀 Average speed: {(performance_stats['domains_processed']/total_time)*60:.1f} domains/minute")

if __name__ == "__main__":
    asyncio.run(main())
