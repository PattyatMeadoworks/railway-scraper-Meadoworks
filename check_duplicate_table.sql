-- Diagnostic for domain_enrich_DUPLICATE table specifically

-- ============================================================
-- 1. VERIFY TABLE EXISTS
-- ============================================================
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'domain_enrich_duplicate'
        ) THEN 'YES - domain_enrich_duplicate table exists'
        ELSE 'NO - domain_enrich_duplicate table does NOT exist'
    END as table_exists;

-- ============================================================
-- 2. CHECK CONSTRAINTS ON DUPLICATE TABLE
-- ============================================================
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
WHERE con.conrelid = 'domain_enrich_duplicate'::regclass
  AND con.contype = 'c';

-- ============================================================
-- 3. COLUMNS IN DUPLICATE TABLE
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'domain_enrich_duplicate'
ORDER BY ordinal_position;

-- ============================================================
-- 4. ROW COUNTS BY STATUS (DUPLICATE TABLE)
-- ============================================================
SELECT 
    enrichment_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 2) as percentage
FROM domain_enrich_duplicate
GROUP BY enrichment_status
ORDER BY count DESC;

-- ============================================================
-- 5. TOTAL SUMMARY (DUPLICATE TABLE)
-- ============================================================
SELECT 
    COUNT(*) as total_domains,
    COUNT(*) FILTER (WHERE enrichment_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE enrichment_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE enrichment_status = 'no_email') as no_email,
    COUNT(*) FILTER (WHERE enrichment_status = 'timeout') as timeout_count,
    COUNT(*) FILTER (WHERE enrichment_status = 'blocked') as blocked_count,
    COUNT(*) FILTER (WHERE enrichment_status = 'error') as error_count
FROM domain_enrich_duplicate;

-- ============================================================
-- 6. CHECK IF GROUP_NUMBER COLUMN EXISTS
-- ============================================================
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'domain_enrich_duplicate' 
            AND column_name = 'group_number'
        ) THEN 'YES - group_number column exists'
        ELSE 'NO - group_number column does NOT exist (need to add it)'
    END as group_column_status;

-- ============================================================
-- 7. IF GROUP COLUMN EXISTS - See group distribution
-- ============================================================
SELECT 
    group_number,
    COUNT(*) as count
FROM domain_enrich_duplicate
WHERE group_number IS NOT NULL
GROUP BY group_number
ORDER BY group_number;

-- ============================================================
-- 8. SAMPLE ROWS (DUPLICATE TABLE)
-- ============================================================
SELECT 
    id,
    domain,
    enrichment_status,
    group_number,
    COALESCE(array_length(emails, 1), 0) as email_count,
    COALESCE(array_length(equipment_types, 1), 0) as equipment_count,
    last_scraped_at
FROM domain_enrich_duplicate
ORDER BY id DESC
LIMIT 10;

