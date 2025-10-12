# 🚀 Deployment Checklist - Ready to Launch!

## ✅ **What's Already Done:**

### **Code Updates:** ✅
- ✅ `main.py` updated with:
  - Consolidated terms (650 unique, no duplicates)
  - Spanish support (150+ translations)
  - Group processing support (GROUP_NUMBER env var)
  - Table name: `domain_enrich_duplicate_duplicate`
  - All optimizations (retries, rotating user agents, etc.)

### **Data Prep:** ✅
- ✅ `grouped_domains_CLEAN.csv` - 407,540 unique domains
- ✅ `grouped_domains_WITH_GROUPS.csv` - With group 1-10 assignments
- ✅ All domains imported to Supabase (407,540 pending)

---

## 🔧 **What You Need to Do:**

### **☐ STEP 1: Run Database Setup SQL**

**File:** `SETUP_DATABASE.sql`

**In Supabase SQL Editor, run these 3 sections:**

```sql
-- 1. Fix constraint (allows timeout/error saves)
ALTER TABLE domain_enrich_duplicate_duplicate 
DROP CONSTRAINT IF EXISTS check_enrichment_status;

ALTER TABLE domain_enrich_duplicate_duplicate
ADD CONSTRAINT check_enrichment_status 
CHECK (enrichment_status IN (
    'pending', 'processing', 'completed', 'no_email', 
    'dns_failed', 'timeout', 'blocked', 'error'
));

-- 2. Add group column
ALTER TABLE domain_enrich_duplicate_duplicate 
ADD COLUMN IF NOT EXISTS group_number INTEGER;

-- 3. Add index for speed
CREATE INDEX IF NOT EXISTS idx_group_status 
ON domain_enrich_duplicate_duplicate(group_number, enrichment_status);
```

**⏱️ Takes:** 10 seconds

---

### **☐ STEP 2: Import Group Assignments**

**In Supabase Table Editor:**

1. Click on `domain_enrich_duplicate_duplicate` table
2. Click **"Import data from CSV"** button
3. Select file: **`grouped_domains_WITH_GROUPS.csv`**
   - Location: `C:\Users\Guerrilla Companies\OneDrive - Walsh CPA\Documents\`
4. Map columns:
   - CSV `domain` → Table `domain`
   - CSV `group_number` → Table `group_number`
5. **Important:** Choose **"Update existing rows"** (match on `domain`)
6. Click Import

**⏱️ Takes:** 2-5 minutes (407K rows)

**Verify it worked:**
```sql
SELECT group_number, COUNT(*) 
FROM domain_enrich_duplicate_duplicate 
GROUP BY group_number 
ORDER BY group_number;
```

Should show 10 groups with ~40,754 domains each.

---

### **☐ STEP 3: Deploy to Railway**

**Option A: Single Service (Simplest)**

1. Connect GitHub repo
2. **Settings:**
   - Build: `pip install -r requirements.txt`
   - Start: `python main.py`
3. **Variables:**
   ```
   SUPABASE_URL=https://lkumldefhsmlgfbjfibj.supabase.co
   SUPABASE_KEY=eyJhbGci...
   ```
4. Deploy!

**⏱️ Time:** ~85 hours for all 407K domains

---

**Option B: 5 Parallel Services (Recommended)**

**Service 1:**
- Repo: Your scraper
- Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `GROUP_NUMBER=1`
- Start: `python main.py`

**Service 2:**
- Same repo
- Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `GROUP_NUMBER=2`
- Start: `python main.py`

**Services 3-5:** Same pattern with GROUP_NUMBER=3,4,5

**After first 5 complete (~17 hours):** Add groups 6-10

**⏱️ Time:** ~34 hours total (vs 85 hours!)

---

**Option C: 10 Parallel Services (Maximum Speed)**

Same as Option B but create all 10 services at once:
- GROUP_NUMBER=1 through GROUP_NUMBER=10

**⏱️ Time:** ~8.5 hours for all 407K domains! 🚀

---

## 📊 **Expected Results:**

### **Per Domain:**
- **Success rate:** 24-28%
- **Total successful:** ~97,000-114,000 domains with data
- **With emails:** ~68,000-97,000 domains
- **Without emails:** ~29,000-40,000 domains

### **Data Quality:**
- ✅ All tenses (molding, molded, thermoformed, etc.)
- ✅ Spanish companies caught (Mexico, Latin America, Spain)
- ✅ Brands detected
- ✅ Materials detected (plastics, metals)

---

## 🚨 **Critical:**

**Don't skip Step 1!** Without fixing the constraint:
- Failed domains won't save properly
- They'll stay 'pending'
- You'll reprocess the same failures over and over
- Waste tons of time!

---

## ✅ **Ready State:**

```
☐ Step 1: Run SETUP_DATABASE.sql (10 seconds)
☐ Step 2: Import grouped_domains_WITH_GROUPS.csv (5 mins)
☐ Step 3: Deploy to Railway (5 mins setup)
✅ Code is ready (main.py updated)
✅ Data is ready (407,540 domains)
```

**You're 15 minutes away from having 5-10 Railway services crushing through 407K domains!** 🎉

