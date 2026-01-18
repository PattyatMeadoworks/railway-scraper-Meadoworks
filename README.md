# Domain Website Scraper

Scrapes domains to find plastics and metalworking equipment keywords, brands, and materials from their websites.

## Features

- Scrapes websites for manufacturing-related keywords
- Detects equipment brands (Haas, Mazak, Engel, etc.)
- Identifies plastics (ABS, PEEK, nylon, etc.)
- Identifies metals (aluminum, stainless steel, titanium, etc.)
- Supports English and Spanish terms
- Saves results to Supabase `domains` table
- Continuous mode for daily scraping of new domains

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase Credentials

Create a `local.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Database Setup

The following columns must exist on your `domains` table:

| Column | Type | Purpose |
|--------|------|---------|
| `website_scraped_at` | timestamp | When the domain was scraped |
| `website_scrape_status` | text | Status: pending, completed, no_keywords, timeout, error |
| `website_keywords` | text[] | Manufacturing keywords found |
| `website_brands` | text[] | Equipment brands found |
| `website_plastics` | text[] | Plastic materials found |
| `website_metals` | text[] | Metal materials found |

SQL to add these columns:

```sql
ALTER TABLE domains 
ADD COLUMN IF NOT EXISTS website_scraped_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS website_scrape_status TEXT DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS website_keywords TEXT[],
ADD COLUMN IF NOT EXISTS website_brands TEXT[],
ADD COLUMN IF NOT EXISTS website_plastics TEXT[],
ADD COLUMN IF NOT EXISTS website_metals TEXT[];

CREATE INDEX IF NOT EXISTS idx_domains_scrape_status 
ON domains(website_scrape_status) 
WHERE website_scrape_status = 'pending' OR website_scrape_status IS NULL;
```

### 4. Test Connection

```bash
python test_supabase_connection.py
```

## Usage

### Single Run (Process All Pending Domains)

```bash
python main.py
```

### Continuous Mode (Daily Scraping)

```bash
python main.py --continuous
```

### Custom Batch Size

```bash
python main.py --batch-size 100
```

### Custom Check Interval (Continuous Mode)

```bash
python main.py --continuous --check-interval 12
```

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet scraped |
| `completed` | Scraped successfully, keywords found |
| `no_keywords` | Scraped successfully, no keywords found |
| `timeout` | Domain unreachable |
| `error` | Invalid domain or other error |

## Performance

- Processes ~50 domains concurrently
- Crawls up to 15 pages per domain
- 60 second timeout per domain
- Typical speed: 30-60 domains/minute

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main scraper |
| `requirements.txt` | Python dependencies |
| `test_local.py` | Test scraper logic locally |
| `test_supabase_connection.py` | Test database connection |
| `local.env` | Your credentials (gitignored) |

## Deployment

### Railway / Digital Ocean

1. Connect your GitHub repo
2. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Start command: `python main.py --continuous`

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["python", "main.py", "--continuous"]
```
