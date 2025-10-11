# Domain Enrichment Web Scraper - Project Context

## 🎯 Project Overview

This is a **Python-based asynchronous web scraper** that enriches business domain data by crawling websites to extract:
- Email addresses
- Equipment types (CNC machining, injection molding, laser cutting, etc.)
- Manufacturer brands (Haas, Engel, Mazak, etc.)
- Manufacturing capabilities keywords
- Materials processed (plastics, metals)

**Data Source:** Supabase PostgreSQL database with ~35,000 domains to process
**Deployment Target:** Digital Ocean droplet (Python environment)
**Current Status:** ⚠️ Code is broken - not processing any domains at all

---

## 📂 Project Files

### Required Files for Review:
1. **`main.py`** - Main scraper code (currently broken)
2. **`requirements.txt`** - Python dependencies
3. **`logs.md`** - Actual deployment logs showing current failures
4. **`CONTEXT.md`** - This file (project documentation)

### Files You'll Create:
- **`main_fixed.py`** - The working version of the scraper

---

## 🗄️ Database Schema (Supabase)

### Table: `domain_enrich`

```sql
CREATE TABLE domain_enrich (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain TEXT UNIQUE NOT NULL,
    emails TEXT[],  -- Array of email addresses
    equipment_types TEXT[],  -- Array of equipment types found
    brands TEXT[],  -- Array of manufacturer brands found
    keywords TEXT[],  -- Array of manufacturing keywords found
    materials JSONB,  -- {"plastics": [], "metals": []}
    enrichment_status TEXT CHECK (enrichment_status IN ('pending', 'processing', 'completed', 'no_email', 'dns_failed', 'timeout', 'blocked', 'error')),
    last_scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Status Values:**
- `pending` - Not yet scraped
- `processing` - Currently being scraped
- `completed` - Successfully scraped with email found
- `no_email` - Successfully scraped but no email found
- `dns_failed` - Domain doesn't exist (DNS lookup failed)
- `timeout` - Domain didn't respond in time
- `blocked` - Domain blocked the scraper
- `error` - Other error occurred

---

## 🚨 Current Problems

### From Recent Deployment (see logs.md):

1. **Code doesn't process ANY domains** (regression from v7.5 → v7.6)
2. **Previous version (v7.5) had these issues:**
   - Only 4.4% success rate (22 out of 500 domains)
   - ~300 DNS failures (but unclear if domains are actually malformed)
   - Duplicate domains being processed
   - Many timeouts

### Key Discussions with User:

**Question 1: DNS Filtering**
- User asked: "Why do I care if they have DNS configured? Many small businesses have working websites but weird DNS setups"
- **IMPORTANT:** Don't aggressively filter out domains based on DNS checks alone. Small businesses often have working websites despite DNS quirks.

**Question 2: Success Rate**
- User confused about why only 15-20% success rate on "valid" domains
- Answer: Many legitimate reasons (timeouts, blocking, no email on site, etc.)
- This is actually normal for web scraping

**Question 3: Current Code**
- Latest version (v7.6) **completely broken** - processes 0 domains
- Need to fix and ensure it actually works

---

## 🎯 What You Need to Do

### Your Mission:
1. **Review** the `logs.md` file to understand actual failure patterns
2. **Review** the current `main.py` code 
3. **Review** the `requirements.txt` to ensure all dependencies are correct
4. **Fix** the code so it:
   - Actually processes domains (not 0!)
   - Handles DNS failures gracefully without being too aggressive
   - Properly handles timeouts and blocking
   - Deduplicates domains before processing
   - Has good error handling and logging
   - Uses async/await properly for performance
   - Processes domains in batches (500 at a time until all ~35K are done)

### Critical Requirements:

#### 1. **Don't Over-Filter Based on DNS**
   - Small businesses may have weird DNS but working websites
   - Try to fetch the website even if DNS check is questionable
   - Only skip if domain is CLEARLY invalid

#### 2. **Handle Multiple URL Variations**
   - Try: `https://domain.com`
   - Try: `https://www.domain.com`
   - Try: `http://domain.com`
   - Try: `http://www.domain.com`
   - Use whichever one works

#### 3. **Proper Concurrency**
   - Use asyncio with semaphore
   - Process 50-100 domains concurrently (adjustable)
   - Don't overwhelm the system

#### 4. **Good Logging**
   - Show progress clearly
   - Log why domains fail (DNS, timeout, blocked, etc.)
   - Show batch progress (Batch 1/70, etc.)

#### 5. **Robust Error Handling**
   - Don't crash on single domain failures
   - Catch and log all exceptions
   - Update database with failure status

#### 6. **Batch Processing Loop**
   ```python
   while True:
       # Fetch 500 pending domains from Supabase
       # Process them concurrently
       # Update database with results
       # If no more pending domains, break
   ```

---

## 🛠️ Technical Stack

### Core Technologies:
- **Python 3.11+**
- **httpx** - Async HTTP client for web requests
- **BeautifulSoup4** - HTML parsing
- **asyncio** - Asynchronous processing
- **supabase-py** - Database client
- **aiodns** - Async DNS resolution (optional, use carefully)

### Performance Targets:
- **50-100 concurrent domains** for optimal speed
- **10-30 second timeout** per domain (configurable)
- **~35,000 total domains** to process
- **Target: 3-6 hours** total runtime for all domains

---

## 📊 Equipment & Brand Detection

### Equipment Categories (200+ types):

**CNC Machining:**
- 5-axis machining, 4-axis machining, 3-axis machining
- CNC turning, CNC milling, Swiss machining
- Vertical machining center, horizontal machining center
- Live tooling

**Injection Molding:**
- Injection molding, insert molding, overmolding
- Multi-shot molding, gas-assist molding
- Micro molding, LSR molding

**Sheet Metal:**
- Laser cutting (fiber, CO2, tube)
- Waterjet cutting
- Press brake, metal forming
- Punching, stamping

**Welding:**
- TIG welding, MIG welding, robotic welding
- Spot welding

**Other:**
- Extrusion, blow molding, thermoforming
- 3D printing, additive manufacturing
- And 100+ more...

### Major Brands (100+ manufacturers):

**CNC/Metalworking:**
- Haas, Mazak, DMG Mori, Okuma, Makino, Fanuc
- Doosan, Hurco, Brother, Fadal, Kitamura

**Injection Molding:**
- Engel, Arburg, Haitian, Sumitomo, Nissei
- Husky, Wittmann Battenfeld, Toyo, Boy, Milacron

**Extrusion:**
- Davis-Standard, Milacron, KraussMaffei
- Battenfeld-Cincinnati, Leistritz

**Materials:**
- **Plastics:** ABS, polycarbonate, nylon, PEEK, PTFE, PVC, polyethylene, polypropylene
- **Metals:** Aluminum, steel, stainless steel, titanium, brass, copper

---

## 📝 Code Structure Reference

### Main Components:

```python
# 1. Equipment/Brand/Keyword definitions
EQUIPMENT_TYPES = [...]  # 200+ equipment types
BRANDS = [...]  # 100+ manufacturer brands
PLASTICS = [...]  # Plastic materials
METALS = [...]  # Metal materials

# 2. Scraping functions
async def scrape_page(url, session):
    """Fetch and parse single page"""
    # Returns: emails, equipment, brands, keywords, materials
    
async def try_url_variations(domain, session):
    """Try http/https and www variations"""
    # Returns: working URL and content
    
async def crawl_business(domain, session):
    """Crawl entire business website (homepage + internal links)"""
    # 1. Try to load homepage
    # 2. Extract internal links
    # 3. Crawl up to 15 internal pages
    # 4. Aggregate all findings
    # 5. Save to Supabase
    
# 3. Batch processing
async def main():
    """Main loop - process all domains"""
    while True:
        # Fetch 500 pending domains
        # Process concurrently with semaphore
        # Update database
        # Check if more pending, else break
```

---

## 🔍 What to Look For in logs.md

When reviewing the logs, identify:

1. **DNS Failures**
   - Are these actually malformed domains?
   - Or legitimate domains with DNS quirks?

2. **Timeout Patterns**
   - Which domains are timing out?
   - Is timeout too aggressive?

3. **Success Patterns**
   - Which domains work?
   - What do successful domains have in common?

4. **Error Messages**
   - Any Python exceptions?
   - Database connection issues?
   - HTTP errors?

5. **Performance Metrics**
   - How many domains per minute?
   - How long does each batch take?

---

## ✅ Success Criteria

The fixed code should:

1. ✅ **Process ALL domains** (not 0, not 22/500, but keep going through all ~35K)
2. ✅ **Achieve 15-30% success rate** (this is normal for web scraping)
3. ✅ **Handle failures gracefully** (don't crash, log properly)
4. ✅ **Not over-filter domains** (try to scrape even with DNS quirks)
5. ✅ **Complete in 3-6 hours** for all 35K domains
6. ✅ **Show clear progress** (batch numbers, success/failure counts)
7. ✅ **Update database correctly** (proper status values)

---

## 💡 Important Notes

### Don't Make These Assumptions:
- ❌ Don't assume DNS failure = bad domain (small business sites often have quirks)
- ❌ Don't assume low success rate = bad code (web scraping is hard)
- ❌ Don't add aggressive pre-filtering (DNS checks should be gentle warnings, not blockers)

### Do These Things:
- ✅ Try multiple URL variations before giving up
- ✅ Log clear failure reasons
- ✅ Handle all exceptions gracefully
- ✅ Show progress clearly
- ✅ Be respectful to websites (don't hammer too hard)

---

## 🚀 Deployment Info

**Environment:** Digital Ocean Droplet (Ubuntu)
**Python Version:** 3.11+
**Run Command:** `python main_fixed.py`
**Logs:** View real-time with `tail -f scraper.log` or in console

**Environment Variables Needed:**
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

---

## 📞 User Preferences

- Prefers **discussion before code changes**
- Wants to **understand the "why"** behind technical decisions
- Values **working code over perfect code**
- Moving to **Cursor IDE** for hands-on debugging
- Wants **clear, actionable feedback**

---

## 🎯 Next Steps for AI Agent

1. Read `logs.md` completely
2. Read `main.py` completely  
3. Read `requirements.txt`
4. Identify root cause of failures
5. Create `main_fixed.py` with:
   - Fix for processing 0 domains
   - Better URL variation handling
   - Less aggressive DNS filtering
   - Proper error handling
   - Clear logging
   - Batch processing loop
6. Test locally if possible
7. Provide deployment instructions

---

## 📚 Past Conversation Context

### Version History:
- **v7.1-7.3**: Early versions with basic scraping
- **v7.4**: Added DNS pre-validation (maybe too aggressive?)
- **v7.5**: Had 4.4% success rate (22/500 domains)
- **v7.6**: Current version - **BROKEN** (0 domains processed)

### Key Insights from Past Chats:
1. Scraper "works really well for first 5 minutes then slows down" - connection pool exhaustion issue
2. User has ~35K domains total to process
3. Processed in batches of 500
4. Originally tried Supabase check constraint that blocked 'error' status (now fixed)
5. User prefers seeing actual progress vs. theoretical optimizations

---

**Good luck! Fix this scraper and make it rock solid. 🚀**