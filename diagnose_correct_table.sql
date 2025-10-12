-- Diagnostic for domain_enrich_duplicate_duplicate table

-- ============================================================
-- 1. TABLE SCHEMA
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'domain_enrich_duplicate_duplicate'
ORDER BY ordinal_position;

-- ============================================================
-- 2. CHECK CONSTRAINTS (What's blocking timeout saves?)
-- ============================================================
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
WHERE con.conrelid = 'domain_enrich_duplicate_duplicate'::regclass
  AND con.contype = 'c';

-- ============================================================
-- 3. TOTAL COUNTS
-- ============================================================
SELECT 
    COUNT(*) as total_domains,
    COUNT(*) FILTER (WHERE enrichment_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE enrichment_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE enrichment_status = 'no_email') as no_email,
    COUNT(*) FILTER (WHERE enrichment_status = 'timeout') as timeout_count,
    COUNT(*) FILTER (WHERE enrichment_status = 'blocked') as blocked_count,
    COUNT(*) FILTER (WHERE enrichment_status = 'error') as error_count
FROM domain_enrich_duplicate_duplicate;

-- ============================================================
-- 4. STATUS BREAKDOWN WITH PERCENTAGES
-- ============================================================
SELECT 
    enrichment_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 2) as percentage
FROM domain_enrich_duplicate_duplicate
GROUP BY enrichment_status
ORDER BY count DESC;

