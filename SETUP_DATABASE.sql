-- ============================================================
-- SETUP SQL FOR domain_enrich_duplicate_duplicate
-- Run these in order in Supabase SQL Editor
-- ============================================================

-- ============================================================
-- STEP 1: Fix Check Constraint (CRITICAL!)
-- This allows the scraper to save failed domains properly
-- ============================================================
ALTER TABLE domain_enrich_duplicate_duplicate 
DROP CONSTRAINT IF EXISTS check_enrichment_status;

ALTER TABLE domain_enrich_duplicate_duplicate
ADD CONSTRAINT check_enrichment_status 
CHECK (enrichment_status IN (
    'pending', 
    'processing', 
    'completed', 
    'no_email', 
    'dns_failed', 
    'timeout', 
    'blocked', 
    'error'
));

-- Verify it worked:
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
WHERE con.conrelid = 'domain_enrich_duplicate_duplicate'::regclass
  AND con.contype = 'c';

-- ============================================================
-- STEP 2: Add group_number Column
-- Allows processing domains in 10 organized groups
-- ============================================================
ALTER TABLE domain_enrich_duplicate_duplicate 
ADD COLUMN IF NOT EXISTS group_number INTEGER;

-- Verify it was added:
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'domain_enrich_duplicate_duplicate'
  AND column_name = 'group_number';

-- ============================================================
-- STEP 3: Create Index for Fast Group Filtering
-- Makes group queries super fast
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_group_status 
ON domain_enrich_duplicate_duplicate(group_number, enrichment_status);

-- Verify index was created:
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'domain_enrich_duplicate_duplicate'
  AND indexname = 'idx_group_status';

-- ============================================================
-- DONE! Now import grouped_domains_WITH_GROUPS.csv
-- ============================================================
-- Next step: In Supabase UI, import the CSV:
-- 1. Go to Table Editor
-- 2. Open domain_enrich_duplicate_duplicate table
-- 3. Click "Import data from CSV"  
-- 4. Select: grouped_domains_WITH_GROUPS.csv
-- 5. Map: domain → domain, group_number → group_number
-- 6. Choose "Update existing rows" (match on domain)
-- 7. Import!

-- After import, verify groups:
SELECT 
    group_number,
    COUNT(*) as domains_in_group
FROM domain_enrich_duplicate_duplicate
GROUP BY group_number
ORDER BY group_number;

-- Should show 10 groups with ~40,754 domains each

