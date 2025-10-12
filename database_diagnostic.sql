-- Database Diagnostic SQL for domain_enrich_duplicate
-- Run these queries in Supabase SQL Editor to help understand your database

-- ============================================================
-- 1. TABLE SCHEMA - See all columns and their types
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'domain_enrich_duplicate'
ORDER BY ordinal_position;

-- ============================================================
-- 2. CHECK CONSTRAINTS - See what values are allowed
-- ============================================================
SELECT 
    con.conname AS constraint_name,
    con.conrelid::regclass AS table_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
WHERE con.conrelid = 'domain_enrich_duplicate'::regclass
  AND con.contype = 'c';  -- c = check constraint

-- ============================================================
-- 3. INDEXES - See what indexes exist
-- ============================================================
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'domain_enrich_duplicate';

-- ============================================================
-- 4. ROW COUNT BY STATUS - Current state
-- ============================================================
SELECT 
    enrichment_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM domain_enrich_duplicate
GROUP BY enrichment_status
ORDER BY count DESC;

-- ============================================================
-- 5. CHECK IF GROUP_NUMBER COLUMN EXISTS
-- ============================================================
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'domain_enrich_duplicate' 
            AND column_name = 'group_number'
        ) THEN 'YES - group_number column exists'
        ELSE 'NO - group_number column does NOT exist'
    END as group_column_status;

-- ============================================================
-- 6. SAMPLE DATA - First 10 rows
-- ============================================================
SELECT 
    id,
    domain,
    enrichment_status,
    COALESCE(array_length(emails, 1), 0) as email_count,
    COALESCE(array_length(equipment_types, 1), 0) as equipment_count,
    COALESCE(array_length(brands, 1), 0) as brand_count
FROM domain_enrich_duplicate
LIMIT 10;

-- ============================================================
-- 7. TOTAL COUNTS
-- ============================================================
SELECT 
    COUNT(*) as total_domains,
    COUNT(*) FILTER (WHERE enrichment_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE enrichment_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE enrichment_status = 'no_email') as no_email,
    COUNT(*) FILTER (WHERE enrichment_status = 'timeout') as timeout_count,
    COUNT(*) FILTER (WHERE enrichment_status = 'error') as error_count
FROM domain_enrich_duplicate;

-- ============================================================
-- 8. CHECK FOR DUPLICATES IN DOMAIN COLUMN
-- ============================================================
SELECT 
    domain,
    COUNT(*) as occurrences
FROM domain_enrich_duplicate
GROUP BY domain
HAVING COUNT(*) > 1
LIMIT 10;

