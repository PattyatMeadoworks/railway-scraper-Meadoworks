# Group Processing Guide

## 🎯 Overview

Your 407,540 domains are divided into **10 equal groups** of ~40,754 domains each.

You can now:
- Process all groups together (default)
- Process specific groups individually
- Run 10 parallel scrapers (one per group!)

---

## 📊 Group Breakdown

```
Group 1: 40,754 domains
Group 2: 40,754 domains
Group 3: 40,754 domains
Group 4: 40,754 domains
Group 5: 40,754 domains
Group 6: 40,754 domains
Group 7: 40,754 domains
Group 8: 40,754 domains
Group 9: 40,754 domains
Group 10: 40,754 domains
```

---

## 🚀 How to Use

### **Option 1: Process All Groups (Default)**

Just run normally:
```bash
python main.py
```

This processes all 407K domains in order.

### **Option 2: Process Specific Group**

Set the `GROUP_NUMBER` environment variable:

**Local (PowerShell):**
```powershell
$env:GROUP_NUMBER="1"
python main.py
```

**Local (local.env file):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
GROUP_NUMBER=1
```

**Railway:**
Add environment variable in Railway dashboard:
- Variable: `GROUP_NUMBER`
- Value: `1` (or 2-10)

### **Option 3: Run 10 Parallel Scrapers** 🚀

Deploy 10 separate Railway services, each with different `GROUP_NUMBER`:

**Service 1:** `GROUP_NUMBER=1`
**Service 2:** `GROUP_NUMBER=2`
...
**Service 10:** `GROUP_NUMBER=10`

**Result:** All 407K domains processed in ~40 minutes! (10x faster!)

---

## 📋 Setup Steps

### **Step 1: Add group_number Column to Supabase**

Run this in Supabase SQL Editor:

```sql
ALTER TABLE domain_enrich_duplicate 
ADD COLUMN IF NOT EXISTS group_number INTEGER;

-- Add index for fast filtering
CREATE INDEX IF NOT EXISTS idx_group_status 
ON domain_enrich_duplicate(group_number, enrichment_status);
```

### **Step 2: Import Group Assignments**

**Option A: CSV Import (Recommended)**
1. Go to Supabase Table Editor
2. Open `domain_enrich_duplicate` table
3. Click "Import data from CSV"
4. Select: `grouped_domains_WITH_GROUPS.csv`
5. Map columns:
   - `domain` → `domain`
   - `group_number` → `group_number`
6. Choose "Update existing rows" (match on `domain`)
7. Import!

**Option B: SQL (Slower)**
Use the generated `update_groups.sql` file (very large, may timeout)

### **Step 3: Verify Groups**

Check in Supabase SQL Editor:

```sql
SELECT group_number, COUNT(*) 
FROM domain_enrich_duplicate 
GROUP BY group_number 
ORDER BY group_number;
```

You should see 10 groups with ~40,754 domains each.

---

## 🎯 Usage Examples

### **Example 1: Process Group 1 Locally**

```powershell
$env:GROUP_NUMBER="1"
python main.py
```

**Output:**
```
🚀 DOMAIN ENRICHMENT SCRAPER v8.0 - MAXIMUM COVERAGE + GROUPS
🎯 GROUP MODE: Processing GROUP 1 only (out of 10 groups)
📡 Fetching pending domains from Supabase...
🎯 Filtering to GROUP 1 only
📊 Found 500 raw domains → 500 unique domains
```

### **Example 2: Deploy Multiple Groups on Railway**

Create 10 Railway services from the same repo:

**railway-scraper-group-1:**
- Environment: `GROUP_NUMBER=1`
- Start command: `python main.py`

**railway-scraper-group-2:**
- Environment: `GROUP_NUMBER=2`
- Start command: `python main.py`

...and so on for groups 3-10.

**Benefit:** All groups processed in parallel = **10x faster!**

### **Example 3: Process All Groups (Default)**

Don't set `GROUP_NUMBER`:

```bash
python main.py
```

Processes all 407K domains sequentially.

---

## 📊 Performance Comparison

| Approach | Time | Cost | Complexity |
|----------|------|------|------------|
| **Single scraper (all groups)** | ~85 hours | Free | Simple |
| **Single scraper (1 group)** | ~8.5 hours | Free | Simple |
| **10 parallel scrapers (Railway)** | ~8.5 hours | $5-10/mo | Medium |

---

## 🔍 Monitoring Progress by Group

### **Check group status:**

```sql
SELECT 
    group_number,
    enrichment_status,
    COUNT(*) as count
FROM domain_enrich_duplicate
GROUP BY group_number, enrichment_status
ORDER BY group_number, enrichment_status;
```

### **See which groups are complete:**

```sql
SELECT 
    group_number,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE enrichment_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE enrichment_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE enrichment_status = 'no_email') as no_email,
    COUNT(*) FILTER (WHERE enrichment_status IN ('completed', 'no_email')) * 100.0 / COUNT(*) as success_rate
FROM domain_enrich_duplicate
GROUP BY group_number
ORDER BY group_number;
```

---

## 💡 Best Practices

### **For Local Testing:**
- Start with Group 1: `$env:GROUP_NUMBER="1"`
- Test on a small group first
- Once working, deploy to Railway for all groups

### **For Production (Railway):**
- Deploy 3-5 parallel services (groups 1-5)
- Monitor for rate limiting
- If no issues, deploy remaining groups (6-10)

### **For Maximum Speed:**
- Deploy all 10 groups in parallel
- Monitor Supabase connection limits
- Each group completes in ~8.5 hours
- Total: All 407K domains in ~8.5 hours!

---

## 🚨 Important Notes

1. **Database constraint must be fixed first!**
   ```sql
   ALTER TABLE domain_enrich_duplicate 
   DROP CONSTRAINT check_enrichment_status;
   
   ALTER TABLE domain_enrich_duplicate
   ADD CONSTRAINT check_enrichment_status 
   CHECK (enrichment_status IN (
       'pending', 'processing', 'completed', 'no_email', 
       'dns_failed', 'timeout', 'blocked', 'error'
   ));
   ```

2. **Import group assignments before running**
   - Use `grouped_domains_WITH_GROUPS.csv`
   - Every domain needs a group_number (1-10)

3. **Don't overlap groups**
   - Each scraper instance should process different group
   - Use GROUP_NUMBER env var to separate them

---

## ✅ Quick Start

```bash
# 1. Add group column to Supabase
ALTER TABLE domain_enrich_duplicate ADD COLUMN group_number INTEGER;

# 2. Import CSV with group assignments
# (Use Supabase UI to import grouped_domains_WITH_GROUPS.csv)

# 3. Run scraper for specific group
$env:GROUP_NUMBER="1"
python main.py

# OR run for all groups
python main.py
```

---

**Now you can process domains in organized groups!** 🎉

