import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import urlparse
import sys
import os
import random
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from local.env file
load_dotenv('local.env')

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL_HERE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🆕 TABLE NAME - Now using duplicate table
TABLE_NAME = "domain_enrich_duplicate_duplicate"

# 🆕 GROUP PROCESSING - Optional: Set GROUP_NUMBER env var to process specific group (1-10)
GROUP_NUMBER = os.getenv("GROUP_NUMBER")  # None = process all, or set to 1-10

# 🆕 ROTATING USER AGENTS - Strategy #2
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Consolidated Manufacturing Terms (650+) - English + Spanish
MANUFACTURING_TERMS = [  # Replaces old EQUIPMENT_TYPES + KEYWORDS
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

# Equipment brands (300+) - Matching N8N v7.0
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
    'rofin', 'trumpf laser', 'bystronic laser', '3d photonics', '4jet',
    
    # Waterjet Cutting
    'omax', 'jet edge', 'wardjet', 'waterjet corporation', 'techni waterjet', 
    'kmt', 'hypertherm', 'esab', 'koike aronson', 'accustream', 'dardi', 
    'waterjet sweden', 'resato',
    
    # Press Brakes & Bending
    'accurpress', 'ermaksan', 'durma', 'safan darley', 'wysong', 'gasparini', 
    'haco', 'baykal', 'dener', 'colgar', 'warcom', 'accurl', 'baileigh',
    'cincinnati', 'jmt usa', 'harsle', 'toyokoki', 'adh machine',
    'wilson tool', 'wila', 'mate precision', 'promecam', 'trumpf tools',
    
    # Shearing Machines
    'accurshear', 'betenbender', 'guifil', 'standard industrial',
    
    # Welding Equipment
    'miller', 'miller electric', 'lincoln electric', 'lincoln', 'hobart',
    'fronius', 'kemppi', 'kjellberg', '2k welding', 'abicor binzel',
    
    # Robotics & Automation
    'panasonic', 'yaskawa', 'motoman', 'fanuc robotics', 'abb robotics', 'kuka',
    'abb', 'otc daihen', 'cloos', 'igm robotics', 'kawasaki', 'abagy', 'agt robotics',
    
    # EDM (Electrical Discharge Machining)
    'sodick', 'charmilles', 'agie', 'agie charmilles', 'aristech', 'mc machinery', 
    'japax', 'joemars', 'ona', 'novick', 'accutex', 'chmer',
    
    # Grinding Machines
    'chevalier', 'kent', 'mitsui', 'jones & shipman', 'boyar schultz', 
    'walter', 'anca', 'reid', 'brown & sharpe', 'thompson', 'landis', 'junker', 
    'kapp', 'agathon',
    
    # Turret Punch & Fabrication
    'strippit', 'finn-power', 'murata', 'wiedemann',
    
    # Stamping & Presses
    'aida', 'komatsu', 'schuler', 'bruderer', 'minster', 'danly', 'verson',
    'clearing', 'niagara', 'bliss', 'arisa', 'chin fong', 'seyi', 'hpm',
    
    # Casting & Foundry
    'inductotherm', 'meltech', 'disa', 'loramendi', 'hunter', 'italpresse',
    'buhler', 'toshiba', 'idra', 'ube', 'toyo', 'frech',
    
    # Tooling & Workholding
    'esi', 'erowa', 'system 3r', 'schunk', 'lang', 'vero-s', 'hainbuch', 'rohm',
    'kitagawa', 'bison', 'buck chuck',
    
    # Injection Molding Machines
    'engel', 'arburg', 'haitian', 'haitian international', 'sumitomo', 
    'sumitomo demag', 'nissei', 'nissei plastic', 'husky', 'wittmann battenfeld', 
    'battenfeld', 'boy', 'boy machines', 'milacron', 'toshiba machine', 
    'shibaura machine', 'chen hsong', 'krauss maffei', 'kraussmaffei', 
    'fanuc roboshot', 'jsw', 'japan steel works', 'negri bossi', 'fu chun shin', 
    'log machine', 'dakumar', 'yizumi', 'tederic', 'bole machinery', 'zhafir', 
    'tianjian', 'demag', 'ferromatik', 'ferromatik milacron', 'van dorn', 
    'netstal', 'sandretto', 'borch', 'guangzhou guanxin', 'guanxin',
    
    # Extrusion Equipment
    'davis-standard', 'davis standard', 'american kuhne', 'cincinnati milacron',
    'graham engineering', 'macro engineering', 'gloucester engineering', 
    'battenfeld-cincinnati', 'battenfeld cincinnati', 'leistritz', 'coperion', 
    'berstorff', 'reifenhauser', 'reifenhäuser', 'windmoller', 'windmöller & hölscher', 
    'w&h', 'bandera', 'starlinger', 'omipa', 'coperion', 'kraussmaffei berstorff',
    'bausano', 'entek', 'nfm welding engineers', 'amut', 'kailida', 'steer engineering',
    'buss', 'windsor machines', 'kabra extrusiontechnik', 'sml maschinengesellschaft',
    'akron extruders', 'welex', 'conair', 'rdn', 'gala', 'maag', 'zerma', 'nrm',
    'diamond america', 'cds', 'eds', 'polytruder', 'greiner', 'american maplan',
    'gloucester', 'erema', 'ngr', 'gamma meccanica', 'kreyenborg', 'reduction engineering',
    
    # Blow Molding Machines
    'kautex', 'kautex maschinenbau', 'bekum', 'bekum america', 'uniloy', 
    'wilmington', 'magic', 'magic mp', 'jomar', 'techne', 'techne packaging',
    'graham', 'r&b plastics', 'plastiblow', 'parker plastic', 'rocheleau',
    'sidel', 'khs', 'corpoplast', 'sipa', 'meccanoplastica', 'st blowmoulding',
    'aoki', 'nissei asb', 'asb', 'bestar', 'meper', 'battenfeld fischer',
    'hayssen', 'impco', 'hartig', 'sterling', 'krupp', 'akei', 'ads', '1blow',
    'siapi', 'flexblow', 'pet technologies', 'turn machine', 'fong kee', 'fki',
    'canmold', 'liberty', 'sika',
    
    # Thermoforming Machines
    'brown machine', 'illig', 'gabler', 'geiss', 'multivac', 'kiefel',
    'formed plastics', 'gn thermoforming', 'wm thermoforming', 'jornen machinery',
    'honghua machinery', 'litai machinery', 'utien pack', 'tz machinery',
    'qingdao xinbeneng', 'asano laboratories', 'comi', 'scm group', 'frimo',
    'qs group', 'irwin', 'maac machinery', 'sencorp', 'scandivac', 'agripak',
    'veripack', 'hamer', 'sencorpwhite', 'zed industries', 'colimatic', 'bmb',
    'plax', 'cannon', 'cmi', 'lyle',
    
    # Rotational Molding
    'persico', 'ferry', 'polivinil', 'caccia', 'rotomachinery', 'fixopan',
    'rotoline', 'reinhardt', 'shuttle', 'rotomachinery group',
    
    # Compression Molding
    'maplan', 'wabash', 'carver', 'french oil', 'dake', 'tung yu', 'rei',
    'daniels', 'greenerd', 'beckwood', 'manning',
    
    # 3D Printing & Additive Manufacturing
    'stratasys', '3d systems', 'hp', 'eos', 'formlabs', 'ultimaker', 'markforged',
    'carbon', 'prusa', 'desktop metal', 'velo3d', 'slm solutions', 'renishaw',
    'concept laser', 'arcam', 'ge additive', '3d.aero',
    
    # Auxiliary Equipment & Material Handling
    'conair', 'novatec', 'motan', 'maguire', 'matsui', 'piovan', 'wittmann',
    'sterling', 'dri-air', 'thermal care', 'advantage engineering', 'aec',
    'auger', 'bd machinery', 'colortronic', 'doteco'
]

# Plastics (200+) - Matching N8N v7.0
PLASTICS = [
    # Commodity Plastics
    'pet', 'pete', 'polyethylene terephthalate',
    'hdpe', 'high-density polyethylene', 'high density polyethylene',
    'ldpe', 'low-density polyethylene', 'low density polyethylene',
    'lldpe', 'linear low-density polyethylene', 'linear low density polyethylene',
    'pp', 'polypropylene', 'homopolymer pp', 'copolymer pp',
    'ps', 'polystyrene', 'hips', 'high impact polystyrene',
    'pvc', 'polyvinyl chloride', 'rigid pvc', 'flexible pvc',
    'eva', 'ethylene vinyl acetate',
    
    # Engineering Plastics
    'abs', 'acrylonitrile butadiene styrene',
    'pa', 'nylon', 'polyamide', 'pa6', 'pa66', 'pa6/6', 'pa6/12', 'pa11', 'pa12',
    'nylon 6', 'nylon 66', 'nylon 6/6', 'nylon 6/12', 'nylon 11', 'nylon 12',
    'pc', 'polycarbonate', 'lexan', 'makrolon',
    'pom', 'acetal', 'delrin', 'polyoxymethylene', 'acetal copolymer', 'acetal homopolymer',
    'pbt', 'polybutylene terephthalate',
    'petg', 'pet-g', 'glycol-modified pet', 'glycol modified polyethylene terephthalate',
    'san', 'styrene acrylonitrile',
    'asa', 'acrylic styrene acrylonitrile', 'acrylonitrile styrene acrylate',
    'pmma', 'acrylic', 'plexiglass', 'acrylic resin',
    'pc/abs', 'pc abs blend',
    
    # High Performance Plastics
    'peek', 'polyetheretherketone', 'poly ether ether ketone',
    'pei', 'ultem', 'polyetherimide',
    'psu', 'polysulfone',
    'pes', 'polyethersulfone',
    'ppsu', 'polyphenylsulfone',
    'pps', 'polyphenylene sulfide', 'ryton',
    'pai', 'polyamide-imide', 'torlon',
    'par', 'polyarylate',
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
    'lsr', 'liquid silicone rubber', 'liquid injection molding silicone',
    'hcr', 'high consistency rubber',
    'rtv', 'room temperature vulcanizing',
    
    # Recycled & Sustainable
    'rpet', 'r-pet', 'recycled pet', 'post-consumer pet',
    'pcr', 'post-consumer recycled', 'post consumer resin', 'post-consumer resin',
    'pir', 'post-industrial recycled', 'post-industrial resin',
    'recycled plastic', 'recycled resin', 'recycled content', 'regrind',
    'bio-based plastic', 'bioplastic', 'pla', 'polylactic acid',
    'pha', 'polyhydroxyalkanoate',
    
    # General Terms
    'resin', 'pellets', 'polymer', 'thermoplastic', 'thermoset',
    'engineering resin', 'commodity resin', 'virgin resin', 'natural resin',
    'glass-filled', 'glass filled', 'fiber-reinforced', 'fiber reinforced',
    'carbon fiber reinforced', 'mineral filled',
    'flame retardant', 'uv stabilized', 'food grade', 'medical grade',
    'fda approved', 'usp class vi',
    
    # Trade Names & Common References
    'noryl', 'valox', 'xenoy', 'cycoloy', 'zytel', 'hytrel',
    'duratec', 'grilamid', 'trogamid', 'vestamid', 'radilon',
    'technyl', 'vydyne', 'akulon', 'stanyl', 'grivory'
]

# Metals (200+) - Matching N8N v7.0
METALS = [
    # Aluminum Alloys
    'aluminum', 'aluminium', 'aluminum alloy', 'aluminium alloy', 'al alloy',
    '6061', '6061-t6', '6061-t4', '6061 aluminum',
    '6063', '6063-t5', '6063-t6', '6063 aluminum',
    '7075', '7075-t6', '7075-t73', '7075 aluminum',
    '5052', '5052 aluminum', '5083', '5083 aluminum',
    '6082', '6082 aluminum', '7050', '7050 aluminum',
    '2024', '2024-t3', '2024-t4', '2024 aluminum',
    '3003', '3003 aluminum', '5086', '5086 aluminum',
    '7050', '7050 aluminum', '2011', '2011 aluminum',
    'cast aluminum', 'a356', 'a380', 'a383', 'aluminum casting',
    'mic-6', 'mic6', 'aluminum tooling plate',
    
    # Carbon & Alloy Steel
    'carbon steel', 'mild steel', 'low carbon steel',
    'alloy steel', 'tool steel', 'spring steel',
    '4140', '4140 steel', '4340', '4340 steel',
    '1018', '1018 steel', '1045', '1045 steel',
    'a36', 'a36 steel', 'a572', 'a572 steel',
    's355', 's355 steel', 'ck45', 'ck45 steel',
    '1020', '1020 steel', '1215', '1215 steel',
    '12l14', '12l14 steel', 'free machining steel',
    '8620', '8620 steel', '4130', '4130 steel',
    'a2 tool steel', 'd2 tool steel', 'o1 tool steel',
    'm2 tool steel', 'h13 tool steel', 's7 tool steel',
    
    # Stainless Steel - Austenitic
    'stainless steel', 'stainless', '304 stainless', '316 stainless',
    '303 stainless', '17-4 stainless', '17-4 ph', '17-4 ph stainless',
    '304l', '304l stainless', '316l', '316l stainless',
    '321 stainless', '310 stainless', '309 stainless',
    '305 stainless', '308 stainless', '347 stainless',
    '301 stainless', '302 stainless',
    'austenitic stainless', 'austenitic stainless steel',
    
    # Stainless Steel - Ferritic & Martensitic
    '410 stainless', '416 stainless', '420 stainless',
    '430 stainless', '440c stainless', '440 stainless',
    '630 stainless', '15-5 ph', '15-5 ph stainless',
    '13-8 ph', '13-8 ph stainless',
    'ferritic stainless', 'martensitic stainless',
    
    # Stainless Steel - Duplex
    'duplex stainless', 'super duplex', 'duplex 2205',
    '2205 stainless', '2507 stainless',
    
    # Brass & Bronze
    'brass', 'brass alloy', 'c36000', 'c360', 'free-cutting brass',
    'c260', 'cartridge brass', 'naval brass', 'c464',
    'bronze', 'bronze alloy', 'phosphor bronze',
    'aluminum bronze', 'silicon bronze', 'tin bronze',
    'copper alloy', 'copper', 'c110', 'c101', 'ofhc copper',
    'beryllium copper', 'beryllium copper alloy', 'c172', 'c17200',
    
    # Titanium
    'titanium', 'titanium alloy', 'ti-6al-4v', 'ti6al4v', 
    'grade 5 titanium', 'grade 2 titanium', 'grade 23 titanium',
    'cp titanium', 'commercially pure titanium',
    'ti-6al-4v eli', 'ti 6-4',
    
    # Nickel Alloys & Superalloys
    'inconel', 'inconel 625', 'inconel 718', 'inconel 600',
    'inconel 601', 'inconel 617', 'inconel 690',
    'hastelloy', 'hastelloy c-276', 'hastelloy x', 'hastelloy c-22',
    'monel', 'monel 400', 'monel k-500',
    'incoloy', 'incoloy 800', 'incoloy 825',
    'nickel alloy', 'nickel', 'nickel 200', 'nickel 201',
    'waspaloy', 'rene 41', 'udimet',
    'nimonic', 'cobalt alloy', 'superalloy',
    
    # Other Metals
    'magnesium', 'magnesium alloy', 'az31', 'az91',
    'zinc', 'zinc alloy', 'zamak', 'zamak 3', 'zamak 5',
    'lead', 'lead alloy',
    'tin', 'tin alloy',
    
    # General Metal Terms
    'heat-treated', 'heat-treated steel', 'heat treating',
    'cold-rolled', 'cold-rolled steel', 'hot-rolled', 'hot-rolled steel',
    'hardened steel', 'annealed', 'normalized',
    'pickled and oiled', 'p&o steel',
    'galvanized steel', 'zinc plated', 'zinc coated',
    'powder coated', 'anodized aluminum', 'anodizing',
    'chromate conversion', 'alodine',
    'passivated stainless', 'passivation',
    'sheet metal', 'plate metal', 'bar stock',
    'round bar', 'square bar', 'hex bar',
    'structural steel', 'i-beam', 'channel', 'angle iron',
    'tube', 'pipe', 'mechanical tubing'
]



EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,})\b', re.IGNORECASE)

# ⚡ Circuit Breaker Constants
MAX_DOMAIN_TIME = 60  # 60 seconds max per domain
MAX_CONSECUTIVE_FAILURES = 3  # Give up after 3 failed pages in a row
MAX_PAGES_PER_DOMAIN = 20

# Performance tracking
performance_stats = {
    'start_time': None,
    'domains_processed': 0,
    'successes': 0,
    'failures': 0,
    'batch_times': [],
    'failure_types': {
        'dns_failed': 0,
        'timeout': 0,
        'blocked': 0,
        'error': 0
    }
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    sys.stdout.flush()

def is_obviously_invalid_domain(domain: str) -> bool:
    """Quick check for obviously invalid domains - no network calls"""
    if not domain or not domain.strip():
        return True
    
    domain = domain.strip().lower()
    
    # Reject obvious garbage
    if domain in ['#na', 'n/a', 'na', '', 'none', 'null']:
        return True
    
    # Reject malformed domains (but be lenient!)
    if 'google.comsearch' in domain or 'search?' in domain:
        return True
    
    # Must have at least one dot
    if '.' not in domain:
        return True
    
    return False

def is_valid_email(email):
    if email.count('@') != 1:
        return False
    invalid = ['.png', '.jpg', '.css', '.js', 'example.com', 'noreply', 'sentry.io']
    return not any(p in email.lower() for p in invalid)

def extract_internal_links(html, base_domain):
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
            parsed = urlparse(url)
            link_domain = parsed.netloc.replace('www.', '')
            
            if link_domain == base_domain.replace('www.', ''):
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                links.append(clean_url)
        except:
            continue
    
    return list(set(links))[:MAX_PAGES_PER_DOMAIN]

def detect_manufacturing(html, url):
    """Detect manufacturing capabilities - Now with Spanish support!"""
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
        if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    # Search plastics (with word boundaries) - FIXED!
    for p in PLASTICS:
        if re.search(r'\b' + re.escape(p) + r'\b', combined, re.IGNORECASE):
            found['plastics'].add(p)
    
    # Search metals (with word boundaries) - FIXED!
    for m in METALS:
        if re.search(r'\b' + re.escape(m) + r'\b', combined, re.IGNORECASE):
            found['metals'].add(m)
    
    return found

async def scrape_page(url, session, retry=0):
    """🆕 Strategy #1: Increased timeouts, Strategy #3: Better error handling"""
    try:
        # Strategy #1: Longer timeouts - 15s/30s instead of 10s/20s
        timeout = 15.0 if retry == 0 else 30.0
        
        response = await session.get(
            url, 
            timeout=timeout,
            follow_redirects=True
        )
        
        # Strategy #3: Handle specific HTTP status codes
        if response.status_code == 429:  # Rate limited
            log(f"    ⏳ Rate limited, waiting 5s...")
            await asyncio.sleep(5)
            if retry < 2:  # Try up to 3 times for rate limits
                return await scrape_page(url, session, retry + 1)
            return None
        elif response.status_code in [502, 503, 504]:  # Server temporarily unavailable
            log(f"    🔄 Server error {response.status_code}, retrying...")
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
        emails = EMAIL_REGEX.findall(html)
        emails = set([e.lower() for e in emails if is_valid_email(e)])
        indicators = detect_manufacturing(html, url)
        
        return {
            'url': url,
            'html': html,
            'emails': emails,
            'indicators': indicators
        }
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
        if retry < 1:
            await asyncio.sleep(1)
            return await scrape_page(url, session, retry + 1)
        return None
    except Exception as e:
        return None

async def try_url_variations(domain, session):
    """🆕 Strategy #1: Retry logic with delays - Try each variation twice!"""
    clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    
    url_variations = [
        f'https://{clean_domain}',
        f'https://www.{clean_domain}',
        f'http://{clean_domain}',
        f'http://www.{clean_domain}',
    ]
    
    # Try all variations TWICE with a delay between attempts
    for attempt in range(2):
        for url in url_variations:
            try:
                result = await scrape_page(url, session)
                if result:
                    log(f"  ✅ Connected via: {url} (attempt {attempt + 1})")
                    return result, url
            except:
                continue
        
        # Between attempts, wait a bit for slow servers
        if attempt == 0:
            await asyncio.sleep(2)
    
    # All variations failed even after retries
    return None, None

async def crawl_business(base_url, session):
    """Crawl business with BETTER failure tracking"""
    clean_domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    domain = clean_domain
    
    # Start domain timer
    domain_start_time = datetime.now()
    consecutive_failures = 0
    
    log(f"🔍 Crawling {domain}")
    
    # 🆕 Strategy #4: Human-like delay between domains
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # STEP 1: Quick obvious-garbage check (no network calls!)
    if is_obviously_invalid_domain(domain):
        log(f"  ❌ Obviously invalid domain format - skipping")
        performance_stats['failures'] += 1
        performance_stats['failure_types']['error'] += 1
        
        try:
            supabase.table(TABLE_NAME).update({
                'enrichment_status': 'error',
                'last_scraped_at': datetime.now().isoformat()
            }).eq('domain', domain).execute()
        except Exception as e:
            log(f"  ⚠️ Failed to save error status: {str(e)}")
        return None
    
    # STEP 2: Try to scrape immediately with retries
    homepage, successful_url = await try_url_variations(domain, session)
    
    if not homepage:
        log(f"  ❌ All URL variations failed - domain unreachable")
        performance_stats['failures'] += 1
        performance_stats['failure_types']['timeout'] += 1
        
        try:
            supabase.table(TABLE_NAME).update({
                'enrichment_status': 'timeout',
                'last_scraped_at': datetime.now().isoformat()
            }).eq('domain', domain).execute()
        except Exception as e:
            log(f"  ⚠️ Failed to save timeout status: {str(e)}")
        return None
    
    # SUCCESS! We got a response
    log(f"  ✅ Homepage loaded successfully")
    
    # Extract and crawl internal links
    internal_links = extract_internal_links(homepage['html'], domain)
    log(f"  📄 Found {len(internal_links)} internal pages to crawl")
    
    # Crawl pages with circuit breaker
    all_pages = [homepage]
    
    for page_url in internal_links:
        # Check domain-level timeout
        elapsed = (datetime.now() - domain_start_time).total_seconds()
        if elapsed > MAX_DOMAIN_TIME:
            log(f"  ⏱️  Domain timeout ({MAX_DOMAIN_TIME}s) - stopping with {len(all_pages)} pages")
            break
        
        # Check consecutive failures
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            log(f"  ⚠️  Too many failures - stopping with {len(all_pages)} pages")
            break
        
        try:
            page_result = await scrape_page(page_url, session)
            if page_result:
                all_pages.append(page_result)
                consecutive_failures = 0  # Reset on success
            else:
                consecutive_failures += 1
        except:
            consecutive_failures += 1
    
    # Aggregate results - EVERYTHING in ONE column!
    all_matches = set()
    all_emails = set()
    
    for page in all_pages:
        if page:
            all_emails.update(page['emails'])
            # Combine EVERYTHING into one set - brands, terms, materials!
            all_matches.update(page['indicators']['manufacturing_terms'])
            all_matches.update(page['indicators']['brands'])
            all_matches.update(page['indicators']['plastics'])
            all_matches.update(page['indicators']['metals'])
    
    total_matches = len(all_matches)
    
    
    log(f"  ✅ {len(all_emails)} emails | {total_matches} matches | {len(all_pages)} pages crawled")
    
    result = {
        'domain': domain,
        'emails': list(all_emails),
        'equipment_types': list(all_matches),  # ALL terms in one column!
        'brands': [],  # Empty - consolidated into equipment_types
        'keywords': [],  # Empty - consolidated into equipment_types
        'materials': {'plastics': [], 'metals': []},  # Empty - consolidated
        'enrichment_status': 'completed' if all_emails else 'no_email',
        'last_scraped_at': datetime.now().isoformat()
    }
    
    # Save to Supabase
    try:
        supabase.table(TABLE_NAME).update(result).eq('domain', domain).execute()
        log(f"  💾 Saved to Supabase")
        performance_stats['successes'] += 1
    except Exception as e:
        log(f"  ❌ Failed to save: {str(e)}")
        performance_stats['failures'] += 1
        
        # Try to at least mark as error
        try:
            supabase.table(TABLE_NAME).update({
                'enrichment_status': 'error',
                'last_scraped_at': datetime.now().isoformat()
            }).eq('domain', domain).execute()
        except:
            pass
    
    return result

async def main():
    """Main scraper - OPTIMIZED VERSION with Strategies 1-6 + Expanded Terms"""
    log("🚀 DOMAIN ENRICHMENT SCRAPER v7.9 - MAXIMUM COVERAGE")
    log(f"📅 Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"🆕 TABLE: {TABLE_NAME}")
    log(f"🔥 CONCURRENCY: 50 (balanced for stability)")
    log(f"⏱️  TIMEOUT: 15s first try, 30s retry per URL")
    log(f"🛑 CIRCUIT BREAKER: 60s per domain, 3 consecutive page failures")
    log(f"📄 PAGES: Up to {MAX_PAGES_PER_DOMAIN} per domain")
    log(f"✨ OPTIMIZATIONS:")
    log(f"   • 2x retry logic with delays")
    log(f"   • Rotating user agents (5 variations)")
    log(f"   • Smart HTTP error handling (429, 502, 503, 504)")
    log(f"   • Human-like delays (0.5-1.5s)")
    log(f"   • Optimized connection pooling")
    log(f"   • Better failure tracking")
    log(f"   • 🆕 EXPANDED TERMS: 484 equipment + 437 keywords (all tenses!)")
    log(f"   • 🆕 Now catches: thermoformed, machined, molded, welded, etc.\n")
    
    performance_stats['start_time'] = datetime.now()
    
    batch_num = 1
    total_processed = 0
    
    while True:
        batch_start = datetime.now()
        
        log(f"\n{'='*60}")
        log(f"📦 BATCH {batch_num}")
        log(f"{'='*60}\n")
        
        # Fetch pending domains
        log("📡 Fetching pending domains from Supabase...")
        
        # 🆕 Optional group filtering
        query = supabase.table(TABLE_NAME).select('domain').eq('enrichment_status', 'pending')
        
        if GROUP_NUMBER:
            query = query.eq('group_number', int(GROUP_NUMBER))
            log(f"🎯 Filtering to GROUP {GROUP_NUMBER} only")
        
        response = query.limit(500).execute()
        
        raw_domains = [row['domain'] for row in response.data if row.get('domain')]
        
        # Clean and deduplicate
        cleaned_domains = []
        seen = set()
        
        for d in raw_domains:
            if not d or not d.strip():
                continue
            
            # Clean and normalize
            clean = d.strip().lower()
            clean = clean.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            # Skip if already seen
            if clean in seen:
                continue
            
            seen.add(clean)
            cleaned_domains.append(clean)
        
        domains = cleaned_domains
        
        if not domains:
            log("\n🎉 ALL DOMAINS PROCESSED!")
            break
        
        log(f"📊 Found {len(raw_domains)} raw domains → {len(domains)} unique domains")
        if len(raw_domains) != len(domains):
            duplicate_count = len(raw_domains) - len(domains)
            log(f"⚠️  Removed {duplicate_count} duplicate domains from batch")
        log(f"🏭 Starting crawl...\n")
        
        # 🆕 Strategy #6: Optimized connection pooling
        # 🆕 Strategy #2: Rotate user agents per batch
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={
                'User-Agent': random.choice(USER_AGENTS),  # Rotate!
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=httpx.Timeout(45.0, connect=15.0),  # Longer overall timeout
            limits=httpx.Limits(
                max_connections=100,  # Reduced from 150
                max_keepalive_connections=20,  # Reduced from 50
                keepalive_expiry=30.0  # Keep connections alive longer
            )
        ) as session:
            
            # 🆕 Strategy #5: Reduced concurrency (50 instead of 100)
            semaphore = asyncio.Semaphore(50)
            results = []
            
            async def crawl_with_limit(domain):
                async with semaphore:
                    result = await crawl_business(f'https://{domain}', session)
                    if result:
                        results.append(result)
                    performance_stats['domains_processed'] += 1
                    return result
            
            tasks = [crawl_with_limit(domain) for domain in domains]
            await asyncio.gather(*tasks)
        
        # Batch complete - calculate stats
        batch_time = (datetime.now() - batch_start).total_seconds()
        performance_stats['batch_times'].append(batch_time)
        
        total_processed += len(domains)
        domains_per_min = (len(domains) / batch_time) * 60 if batch_time > 0 else 0
        
        # Log batch completion with performance metrics
        log(f"\n{'='*60}")
        log(f"✅ BATCH {batch_num} COMPLETE!")
        log(f"{'='*60}")
        log(f"⏱️  Batch time: {batch_time:.1f}s")
        log(f"🚀 Speed: {domains_per_min:.1f} domains/minute")
        
        if performance_stats['domains_processed'] > 0:
            success_rate = (performance_stats['successes']/performance_stats['domains_processed']*100)
            log(f"📊 Success rate: {success_rate:.1f}%")
        else:
            log(f"📊 Success rate: 0.0%")
            
        log(f"📈 Total processed: {total_processed} domains")
        
        # Calculate overall stats
        total_time = (datetime.now() - performance_stats['start_time']).total_seconds()
        overall_rate = (total_processed / total_time) * 60 if total_time > 0 else 0
        log(f"📊 Overall rate: {overall_rate:.1f} domains/minute")
        
        log("")
        
        if domains:
            log(f"⏸️  Cooldown: 5 seconds before next batch...\n")
            await asyncio.sleep(5)
        
        batch_num += 1
    
    # Final summary
    total_time = (datetime.now() - performance_stats['start_time']).total_seconds()
    log(f"\n{'='*60}")
    log(f"🎉 ALL DOMAINS PROCESSED!")
    log(f"{'='*60}")
    log(f"⏱️  Total time: {total_time/60:.1f} minutes")
    log(f"📊 Total domains: {total_processed}")
    log(f"✅ Successes: {performance_stats['successes']}")
    log(f"❌ Failures: {performance_stats['failures']}")
    log(f"")
    log(f"📋 Failure Breakdown:")
    if performance_stats['failures'] > 0:
        log(f"   🔍 DNS Failed: {performance_stats['failure_types']['dns_failed']} ({performance_stats['failure_types']['dns_failed']/performance_stats['failures']*100:.1f}%)")
        log(f"   ⏱️  Timeout: {performance_stats['failure_types']['timeout']} ({performance_stats['failure_types']['timeout']/performance_stats['failures']*100:.1f}%)")
        log(f"   🚫 Blocked: {performance_stats['failure_types']['blocked']} ({performance_stats['failure_types']['blocked']/performance_stats['failures']*100:.1f}%)")
        log(f"   ❌ Error: {performance_stats['failure_types']['error']} ({performance_stats['failure_types']['error']/performance_stats['failures']*100:.1f}%)")
    else:
        log(f"   🔍 DNS Failed: 0")
        log(f"   ⏱️  Timeout: 0")
        log(f"   🚫 Blocked: 0")
        log(f"   ❌ Error: 0")
    log(f"")
    log(f"🚀 Average speed: {(total_processed/total_time)*60:.1f} domains/minute")
    log(f"\n💡 TIP: To retry failed domains, change 'pending' to 'timeout' in the query and run again!")

if __name__ == "__main__":
    asyncio.run(main())

