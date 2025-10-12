# Local Setup Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Supabase Credentials

Edit `local.env` file and add your credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

**Important:** The `local.env` file is already in `.gitignore` so your credentials won't be committed!

## 3. Test Locally

### Quick test (no database):
```bash
python test_local.py
```

### Full scraper (requires Supabase):
```bash
python main_fixed.py
```

## 4. Deploy to Production

When deploying to Digital Ocean:

1. **Option A:** Set environment variables on the server:
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your-anon-key"
   ```

2. **Option B:** Copy `local.env` to the server (but keep it secure!)
   ```bash
   scp local.env user@your-server:/path/to/scraper/
   ```

3. Run the scraper:
   ```bash
   python main.py
   ```

## File Structure

```
scraper/
├── main.py              # Main scraper (copy main_fixed.py here)
├── main_fixed.py        # Fixed version (use this!)
├── local.env            # Your credentials (gitignored)
├── requirements.txt     # Python dependencies
├── test_local.py        # Quick local test
├── .gitignore          # Protects your credentials
└── SETUP.md            # This file
```

## Security Notes

✅ **Safe to commit:**
- `main.py`
- `requirements.txt`
- `.gitignore`
- `SETUP.md`

❌ **NEVER commit:**
- `local.env` (contains credentials)
- `main_fixed.py` (temporary file, copy to main.py instead)

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "SUPABASE_URL not set" error
Make sure `local.env` exists and contains valid credentials.

### "No domains processed"
Check your Supabase table has domains with `enrichment_status = 'pending'`

