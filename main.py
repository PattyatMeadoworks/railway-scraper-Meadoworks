import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import urlparse
import sys
import os
import psutil  # For monitoring system resources
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL_HERE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Complete equipment types (200+) - Matching N8N v7.0
EQUIPMENT_TYPES = [
    # CNC Machining - General & Service terms
    '5-axis machining', '4-axis machining', '3-axis machining', 'multi-axis machining',
    'cnc machining services', 'cnc machining capabilities', 'precision machining', 'precision machining services',
    'cnc turning', 'cnc turning services', 'cnc turning capabilities',
    'cnc milling', 'cnc milling services', 'cnc milling capabilities',
    'swiss machining', 'swiss-type machining', 'swiss machining services', 'swiss screw machining',
    'vertical machining center', 'horizontal machining center',
    'turning services', 'milling services', 'machining services', 'precision turning',
    'live tooling', 'live tooling capabilities',
    
    # Laser Cutting - General & Service terms
    'laser cutting', 'laser cutting services', 'laser cutting capabilities',
    'fiber laser cutting', 'fiber laser cutting services',
    'co2 laser cutting', 'co2 laser cutting services',
    'tube laser cutting', 'tube laser cutting services',
    '3d laser cutting', 'laser cutting and fabrication', 'metal laser cutting',
    
    # Waterjet Cutting - General & Service terms
    'waterjet cutting', 'waterjet cutting services', 'waterjet cutting capabilities',
    'abrasive waterjet cutting', 'water jet cutting',
    
    # Press Brake & Forming - General & Service terms
    'press brake', 'press brake services', 'press brake capabilities',
    'metal forming', 'metal forming services', 'metal forming capabilities',
    'bending services', 'cnc bending', 'precision bending', 'precision bending services',
    'brake press services',
    
    # Sheet Metal Fabrication
    'sheet metal fabrication', 'sheet metal fabrication services',
    'sheet metal services', 'metal fabrication', 'metal fabrication services',
    'custom metal fabrication',
    'cnc punching', 'cnc punching services', 'turret punching', 'turret punching services',
    'punching capabilities',
    
    # Welding - General & Service terms
    'welding', 'welding services', 'welding capabilities',
    'mig welding', 'mig welding services',
    'tig welding', 'tig welding services',
    'robotic welding', 'robotic welding services', 'robotic welding capabilities',
    'laser welding', 'laser welding services',
    'spot welding', 'arc welding', 'arc welding services',
    
    # EDM - General & Service terms
    'wire edm', 'wire edm services', 'wire edm capabilities',
    'sinker edm', 'sinker edm services',
    'ram edm', 'ram edm services',
    'edm services', 'edm capabilities',
    'electrical discharge machining',
    
    # Grinding - General & Service terms
    'grinding', 'grinding services', 'grinding capabilities',
    'precision grinding', 'precision grinding services',
    'surface grinding', 'surface grinding services',
    'cylindrical grinding', 'cylindrical grinding services',
    'centerless grinding', 'centerless grinding services',
    
    # Stamping & Die - General & Service terms
    'metal stamping', 'metal stamping services', 'metal stamping capabilities',
    'progressive die stamping', 'stamping', 'stamping services', 'stamping capabilities',
    'tool and die', 'tool and die services', 'tool and die capabilities',
    'mold making', 'mold making services', 'tooling', 'tooling services',
    'die making', 'die making services',
    
    # Casting - General & Service terms
    'die casting', 'die casting services', 'die casting capabilities',
    'investment casting', 'investment casting services',
    'sand casting', 'sand casting services',
    'aluminum die casting', 'aluminum die casting services',
    'casting', 'casting services', 'casting capabilities',
    
    # Injection Molding - General & Service terms
    'injection molding', 'injection molding services', 'injection molding capabilities',
    'custom injection molding', 'contract molding', 'contract molding services',
    'plastic injection molding', 'plastic injection',
    'insert molding', 'insert molding services', 'insert molding capabilities',
    'overmolding', 'overmolding services', 'overmolding capabilities',
    'two-shot molding', 'two-shot molding services', 'two-shot injection molding',
    '2k molding', '2-shot molding',
    'multi-component molding', 'multi-shot molding',
    'lsr molding', 'lsr molding services', 'liquid silicone rubber molding',
    'micro molding', 'micro molding services',
    
    # Extrusion - General & Service terms
    'extrusion', 'extrusion services', 'extrusion capabilities',
    'profile extrusion', 'profile extrusion services',
    'pipe extrusion', 'pipe extrusion services',
    'sheet extrusion', 'sheet extrusion services',
    'plastic extrusion', 'plastic extrusion services',
    'blown film', 'blown film extrusion',
    'co-extrusion', 'co-extrusion services',
    
    # Blow Molding - General & Service terms
    'blow molding', 'blow molding services', 'blow molding capabilities',
    'extrusion blow molding', 'extrusion blow molding services',
    'injection blow molding', 'injection blow molding services',
    'stretch blow molding', 'stretch blow molding services',
    'pet blow molding', 'bottle manufacturing',
    
    # Thermoforming - General & Service terms
    'thermoforming', 'thermoforming services', 'thermoforming capabilities',
    'vacuum forming', 'vacuum forming services',
    'pressure forming', 'pressure forming services',
    'heavy gauge thermoforming', 'thin gauge thermoforming',
    
    # Rotomolding - General & Service terms
    'rotomolding', 'rotomolding services', 'rotomolding capabilities',
    'rotational molding', 'rotational molding services',
    'roto molding',
    
    # Compression Molding - General & Service terms
    'compression molding', 'compression molding services', 'compression molding capabilities',
    'smc molding', 'bmc molding', 'composite molding',
    
    # Additive Manufacturing - General & Service terms
    '3d printing', '3d printing services', '3d printing capabilities',
    'additive manufacturing', 'additive manufacturing services', 'additive manufacturing capabilities',
    'metal 3d printing', 'metal 3d printing services',
    'rapid prototyping', 'rapid prototyping services', 'prototype development'
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

# Keywords - Matching N8N v7.0
KEYWORDS = [
    # CNC & Machining
    'cnc', 'machining', 'machine shop', 'machinist', 'mill', 'lathe', 'turning', 'milling',
    'vmc', 'hmc', '3-axis', '4-axis', '5-axis', 'multi-axis', 'swiss-type',
    'live tooling', 'cnc lathe', 'cnc mill', 'precision machining',
    
    # Laser & Cutting
    'laser', 'laser cutting', 'fiber laser', 'co2 laser', 'tube laser',
    'laser engraving', 'laser marking', 'laser welding',
    
    # Waterjet
    'waterjet', 'water jet', 'abrasive jet', 'waterjet cutting',
    
    # Press & Forming
    'press brake', 'bending', 'metal forming', 'forming', 'brake press',
    'shearing', 'guillotine', 'power shear', 'hydraulic press',
    
    # Welding
    'welding', 'welder', 'weld', 'mig', 'tig', 'arc welding',
    'spot welding', 'robotic welding', 'weld automation',
    
    # EDM
    'edm', 'electrical discharge', 'wire edm', 'sinker edm', 'ram edm',
    
    # Grinding
    'grinding', 'grinder', 'surface grinder', 'cylindrical grinder',
    'od grinding', 'id grinding', 'centerless grinding',
    
    # Sheet Metal & Fabrication
    'sheet metal', 'metal fabrication', 'fabrication', 'turret punch', 'punching',
    'laser cutting', 'metal stamping', 'fab shop',
    
    # Stamping & Die
    'stamping', 'metal stamping', 'progressive die', 'die stamping',
    'transfer die', 'compound die',
    
    # Casting & Foundry
    'casting', 'foundry', 'die casting', 'sand casting', 'investment casting',
    'lost wax', 'permanent mold',
    
    # Tooling
    'tooling', 'tool and die', 'mold making', 'die making', 'tool design',
    'jigs and fixtures',
    
    # Plastic Processing - Injection Molding
    'injection molding', 'plastic injection', 'molding', 'imm',
    'insert molding', 'overmolding', 'two-shot', '2k molding', '2-shot',
    'multi-shot', 'micro molding', 'thin wall molding',
    
    # Plastic Processing - Extrusion
    'extrusion', 'extruder', 'plastic extrusion', 'blown film', 'profile extrusion',
    'pipe extrusion', 'sheet extrusion', 'co-extrusion',
    
    # Plastic Processing - Blow Molding
    'blow molding', 'blow moulding', 'bottle', 'container', 'pet blow',
    'extrusion blow molding', 'injection blow molding', 'stretch blow molding',
    
    # Plastic Processing - Thermoforming
    'thermoforming', 'vacuum forming', 'pressure forming',
    'heavy gauge thermoforming', 'thin gauge thermoforming',
    
    # Plastic Processing - Rotomolding
    'rotomolding', 'rotational molding', 'roto molding',
    
    # Plastic Processing - Compression Molding
    'compression molding', 'smc', 'bmc', 'composite molding',
    
    # Additive Manufacturing
    '3d printing', 'additive manufacturing', 'fdm', 'sla', 'sls', 
    'rapid prototyping', 'metal 3d printing', 'dmls', 'slm',
    
    # Quality & Metrology
    'cmm', 'coordinate measuring', 'inspection', 'quality control',
    'optical inspection', 'vision system', 'metrology',
    
    # Surface Treatment
    'anodizing', 'plating', 'powder coating', 'painting',
    'heat treating', 'passivation', 'electropolishing',
    
    # Assembly & Secondary
    'assembly', 'kitting', 'packaging', 'sub-assembly',
    'ultrasonic welding', 'heat staking', 'press fit'
]

EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9._+-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,})\b', re.IGNORECASE)

# Performance tracking
performance_stats = {
    'start_time': None,
    'domains_processed': 0,
    'successes': 0,
    'failures': 0,
    'batch_times': []
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    sys.stdout.flush()

def log_system_stats():
    """Log current system resource usage"""
    try:
        process = psutil.Process()
        
        # Memory info
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / 1024 / 1024
        
        # CPU info
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # File descriptors (connections)
        try:
            num_fds = process.num_fds()
        except:
            num_fds = "N/A (Windows)"
        
        # System-wide memory
        system_mem = psutil.virtual_memory()
        
        log(f"📊 SYSTEM STATS:")
        log(f"   💾 Memory: {mem_mb:.1f}MB / {system_mem.total/1024/1024/1024:.1f}GB total ({system_mem.percent}% used)")
        log(f"   🔌 File Descriptors: {num_fds}")
        log(f"   🖥️  CPU: {cpu_percent}%")
        
    except Exception as e:
        log(f"⚠️  Could not get system stats: {e}")

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
    
    return list(set(links))[:20]  # Max 20 pages

def detect_manufacturing(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text().lower()
    combined = text + ' ' + url.lower()
    
    found = {
        'equipment': set(),
        'brands': set(),
        'keywords': set(),
        'plastics': set(),
        'metals': set()
    }
    
    for eq in EQUIPMENT_TYPES:
        if eq in combined:
            found['equipment'].add(eq)
    
    for brand in BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', combined, re.IGNORECASE):
            found['brands'].add(brand)
    
    for kw in KEYWORDS:
        if kw in combined:
            found['keywords'].add(kw)
    
    for p in PLASTICS:
        if re.search(r'\b' + re.escape(p) + r'\b', combined, re.IGNORECASE):
            found['plastics'].add(p)
    
    for m in METALS:
        if re.search(r'\b' + re.escape(m) + r'\b', combined, re.IGNORECASE):
            found['metals'].add(m)
    
    return found

async def scrape_page(url, session, retry=0):
    """Scrape single page with retry logic"""
    try:
        response = await session.get(
            url, 
            timeout=30.0,
            follow_redirects=True
        )
        
        if response.status_code >= 400:
            if retry < 2:
                await asyncio.sleep(2)
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
        if retry < 2:
            await asyncio.sleep(2)
            return await scrape_page(url, session, retry + 1)
        return None
    except Exception as e:
        return None

async def try_url_variations(domain, session):
    """Try multiple URL variations to find one that works"""
    clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '')
    
    url_variations = [
        f'https://{clean_domain}',
        f'https://www.{clean_domain}',
        f'http://{clean_domain}',
        f'http://www.{clean_domain}',
    ]
    
    for url in url_variations:
        try:
            result = await scrape_page(url, session)
            if result:
                log(f"  ✅ Successfully connected using: {url}")
                return result, url
        except:
            continue
    
    return None, None

async def crawl_business(base_url, session):
    """Crawl entire business website"""
    clean_domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '')
    domain = clean_domain
    log(f"🔍 Crawling {domain}")
    
    homepage, successful_url = await try_url_variations(domain, session)
    
    if not homepage:
        log(f"  ❌ Failed to load {domain} (tried all URL variations)")
        performance_stats['failures'] += 1
        return None
    
    internal_links = extract_internal_links(homepage['html'], domain)
    log(f"  📄 Found {len(internal_links)} pages to crawl")
    
    tasks = [scrape_page(link, session) for link in internal_links]
    results = await asyncio.gather(*tasks)
    
    all_pages = [homepage] + [r for r in results if r]
    
    agg = {
        'emails': set(),
        'equipment': set(),
        'brands': set(),
        'keywords': set(),
        'plastics': set(),
        'metals': set()
    }
    
    for page in all_pages:
        if page:
            agg['emails'].update(page['emails'])
            agg['equipment'].update(page['indicators']['equipment'])
            agg['brands'].update(page['indicators']['brands'])
            agg['keywords'].update(page['indicators']['keywords'])
            agg['plastics'].update(page['indicators']['plastics'])
            agg['metals'].update(page['indicators']['metals'])
    
    total_matches = sum([len(agg[k]) for k in ['equipment', 'brands', 'keywords', 'plastics', 'metals']])
    
    log(f"  ✅ {len(agg['emails'])} emails | {total_matches} matches | {len(all_pages)} pages")
    
    result = {
        'domain': domain,
        'emails': list(agg['emails']),
        'equipment_types': list(agg['equipment']),
        'brands': list(agg['brands']),
        'keywords': list(agg['keywords']),
        'materials': {
            'plastics': list(agg['plastics']),
            'metals': list(agg['metals'])
        },
        'enrichment_status': 'completed' if agg['emails'] else 'no_email',
        'last_scraped_at': datetime.now().isoformat()
    }
    
    # Save to Supabase
    try:
        supabase.table('domain_enrich').update(result).eq('domain', domain).execute()
        log(f"  💾 Saved to Supabase")
        performance_stats['successes'] += 1
    except Exception as e:
        log(f"  ❌ Failed to save: {str(e)}")
        performance_stats['failures'] += 1
    
    return result

async def main():
    """Main scraper with aggressive performance testing"""
    log("🚀 DOMAIN ENRICHMENT SCRAPER v7.2 - PERFORMANCE TEST MODE")
    log(f"📅 Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"🔥 CONCURRENCY: 200 (AGGRESSIVE TEST)")
    log(f"⏱️  TIMEOUT: 30s per request")
    log(f"📄 PAGES: Up to 20 per domain\n")
    
    performance_stats['start_time'] = datetime.now()
    
    batch_num = 1
    total_processed = 0
    
    while True:
        batch_start = datetime.now()
        
        log(f"\n{'='*60}")
        log(f"📦 BATCH {batch_num}")
        log(f"{'='*60}\n")
        
        # Log system stats at start of batch
        log_system_stats()
        log("")
        
        # Fetch pending domains
        log("📡 Fetching pending domains from Supabase...")
        response = supabase.table('domain_enrich').select('domain').eq('enrichment_status', 'pending').limit(500).execute()
        
        domains = [row['domain'] for row in response.data if row.get('domain')]
        
        if not domains:
            log("\n🎉 ALL DOMAINS PROCESSED!")
            break
        
        log(f"📊 Found {len(domains)} pending domains in this batch\n")
        log("🏭 Starting crawl...\n")
        
        # Create ONE shared client for the entire batch
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=250, max_keepalive_connections=50)  # INCREASED LIMITS
        ) as session:
            
            # Process with HIGH concurrency
            semaphore = asyncio.Semaphore(200)  # 🔥 200 CONCURRENT!
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
        log(f"📊 Success rate: {(performance_stats['successes']/performance_stats['domains_processed']*100):.1f}%")
        log(f"📈 Total processed: {total_processed} domains")
        
        # Calculate overall stats
        total_time = (datetime.now() - performance_stats['start_time']).total_seconds()
        overall_rate = (total_processed / total_time) * 60 if total_time > 0 else 0
        log(f"📊 Overall rate: {overall_rate:.1f} domains/minute")
        
        # Log system stats at end of batch
        log("")
        log_system_stats()
        
        # Cooldown between batches
        if domains:
            log(f"\n⏸️  Cooldown: 5 seconds before next batch...\n")
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
    log(f"🚀 Average speed: {(total_processed/total_time)*60:.1f} domains/minute")

if __name__ == "__main__":
    asyncio.run(main())