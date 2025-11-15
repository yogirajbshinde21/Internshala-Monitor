# 📝 SETUP INSTRUCTIONS - Internshala Monitor

## Quick Start Guide

### Step 1: Set Up Gmail App Password (IMPORTANT!)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account: https://myaccount.google.com/
   - Click "Security" on the left
   - Under "How you sign in to Google", enable "2-Step Verification"

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Windows Computer" (or "Other")
   - Click "Generate"
   - Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
   - **Save this password** - you'll need it for the .env file

### Step 2: Create .env File

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your details:
   ```env
   EMAIL_ADDRESS=yourname@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Your App Password (16 chars)
   RECIPIENT_EMAIL=yourname@gmail.com
   ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test the System

1. **Test the scraper:**
   ```bash
   python scraper.py
   ```
   Should find and list internships from Internshala.

2. **Test email sending:**
   ```bash
   python email_sender.py
   ```
   Should send a test email to your recipient address.

3. **Run the full system:**
   ```bash
   python main.py
   ```

### Step 5: Customize Your Preferences

Edit `config.json` to match your needs:

```json
{
  "keywords": ["full stack", "mern", "react", "node"],
  "locations": ["Mumbai", "Work From Home", "Your City"],
  "min_stipend": 5000,
  "check_interval_minutes": 120
}
```

### Step 6: Set Up GitHub Actions (Optional)

For automated monitoring every 2 hours:

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/internshala-monitor.git
   git push -u origin main
   ```

2. **Add Repository Secrets:**
   - Go to your GitHub repo
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add these three secrets:
     - `EMAIL_ADDRESS` = your Gmail address
     - `EMAIL_PASSWORD` = your Gmail App Password
     - `RECIPIENT_EMAIL` = email to receive notifications

3. **Enable GitHub Actions:**
   - Go to the Actions tab
   - Click "I understand my workflows, go ahead and enable them"

4. **Manual Trigger:**
   - Go to Actions → Internshala Monitor
   - Click "Run workflow"
   - Click the green "Run workflow" button

## ⚠️ Troubleshooting

### "Email authentication failed"
- Make sure you're using an **App Password**, not your regular Gmail password
- Verify 2-Factor Authentication is enabled on your Google account
- Check for typos in your .env file

### "No module named 'requests'"
- Run: `pip install -r requirements.txt`
- Or activate your virtual environment first

### "No internships found"
- Your filters might be too strict
- Try increasing the locations list
- Lower the `min_stipend` value
- Check your internet connection

### "config.json not found"
- Make sure you're running from the project root directory
- Verify the file exists: `ls config.json` (Linux/Mac) or `dir config.json` (Windows)

### GitHub Actions not running
- Check that secrets are set correctly (no extra spaces)
- Verify the workflow file is in `.github/workflows/monitor.yml`
- Check the Actions tab for error logs

## 📊 Expected Output

When running `python main.py`, you should see:

```
============================================================
🔍 INTERNSHALA INTERNSHIP MONITOR
============================================================

📋 Configuration loaded:
   Locations: Mumbai, Thane, Work From Home...
   Min Stipend: ₹5000

🔍 Starting internship search...
📡 Fetching: https://internshala.com/internships/...
✅ Found 40 internships using selector: div {'class': 'individual_internship'}
  ✅ New: Full Stack Developer at Company XYZ - Mumbai
  ✅ New: MERN Stack Intern at Startup ABC - Work from home
  ...

============================================================
✅ SUCCESS: Found 2 new internship(s)
============================================================

📊 Summary of new internships:
1. Full Stack Developer at Company XYZ
   💰 ₹15,000/month | 📍 Mumbai
2. MERN Stack Intern at Startup ABC
   💰 ₹10,000/month | 📍 Work from home

📧 Sending email notification...
✅ Email notification sent successfully!
```

## 🎯 Next Steps

1. ✅ Verify scraper works: `python scraper.py`
2. ✅ Test email: `python email_sender.py`
3. ✅ Run full system: `python main.py`
4. ✅ Customize `config.json` with your preferences
5. ✅ Set up GitHub Actions for automation
6. ✅ Check your email for notifications!

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Review the error messages - they're designed to be helpful
- Verify all environment variables are set correctly
- Make sure all files are in the correct locations

---

**Happy internship hunting!** 🚀
