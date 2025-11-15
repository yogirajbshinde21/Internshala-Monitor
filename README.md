# 🚀 Internshala Internship Auto-Monitor & Email Notification System

An automated Python system that monitors Internshala for new full-stack developer internships and sends email notifications when opportunities matching your preferences are posted.

## ✨ Features

- 🔍 **Automated Scraping**: Monitors Internshala internship listings automatically
- 📧 **Email Notifications**: Sends beautiful HTML emails with new opportunities
- 🎯 **Smart Filtering**: Filters by location, stipend, and keywords
- 🔄 **Duplicate Prevention**: Tracks seen internships to avoid spam
- ⚙️ **GitHub Actions**: Runs automatically every 2 hours
- 🛡️ **Robust Error Handling**: Handles network failures and HTML structure changes

## 📋 Prerequisites

- Python 3.10 or higher
- Gmail account with App Password enabled
- GitHub account (for automation)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd internshala-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your credentials
   ```

4. **Configure Gmail App Password**
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or Other)
   - Copy the 16-character password
   - Add it to your `.env` file

## ⚙️ Configuration

Edit `config.json` to customize your preferences:

```json
{
  "search_categories": [
    "web-development",
    "software-development",
    "information-technology",
    "javascript-development",
    "python/django-development",
    "node.js-development",
    "full-stack-development"
  ],
  "keywords": ["full stack", "mern stack", "web development"],
  "locations": ["Mumbai", "Thane", "Work From Home"],
  "min_stipend": 5000,
  "check_interval_minutes": 120
}
```

**Important**: The `search_categories` field determines which internship categories to search on Internshala. You can add or remove categories based on your interests. Each category corresponds to a URL like `https://internshala.com/internships/{category}-internship/`

## 🚀 Usage

### Local Testing

Run the scraper manually:
```bash
python main.py
```

Test email sending:
```bash
python email_sender.py
```

Test scraper only:
```bash
python scraper.py
```

### GitHub Actions (Automated)

1. **Set up repository secrets**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
     - `EMAIL_ADDRESS`: Your Gmail address
     - `EMAIL_PASSWORD`: Your Gmail App Password
     - `RECIPIENT_EMAIL`: Email to receive notifications

2. **Enable Actions**
   - Go to the Actions tab
   - Enable workflows if prompted

3. **Manual trigger**
   - Go to Actions → Internshala Monitor
   - Click "Run workflow"

The workflow runs automatically every 2 hours.

## 📁 Project Structure

```
internshala-monitor/
├── main.py                  # Main orchestrator
├── scraper.py               # Web scraping logic
├── email_sender.py          # Email notification system
├── config.json              # User preferences
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # Documentation
├── data/
│   └── seen_internships.json  # Tracking seen opportunities
└── .github/
    └── workflows/
        └── monitor.yml     # GitHub Actions workflow
```

## 🔍 How It Works

1. **Scraping**: Fetches internship listings from Internshala
2. **Filtering**: Applies your preferences (location, stipend, keywords)
3. **Duplicate Check**: Compares with previously seen internships
4. **Notification**: Sends email for new matching opportunities
5. **Persistence**: Saves seen internship IDs to avoid duplicates

## 🛠️ Troubleshooting

### Email not sending
- Verify Gmail App Password is correct
- Check if 2-factor authentication is enabled
- Ensure `.env` file exists and has correct values

### No internships found
- Check if Internshala's HTML structure has changed
- Verify your internet connection
- Check filter criteria in `config.json`

### GitHub Actions not running
- Verify secrets are set correctly
- Check Actions tab for error logs
- Ensure workflow file is in `.github/workflows/`

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_ADDRESS` | Your Gmail address | `yourname@gmail.com` |
| `EMAIL_PASSWORD` | Gmail App Password (16 chars) | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Email to receive notifications | `yourname@gmail.com` |

## ⚠️ Important Notes

- **App Password Required**: Gmail requires an App Password, not your regular password
- **Rate Limiting**: Scrapes responsibly with proper delays
- **Personal Use**: This tool is for personal use only
- **HTML Changes**: Internshala may update their website; selectors may need updates

## 🔄 Updates & Maintenance

If Internshala changes their website structure:
1. Inspect the page elements using browser DevTools
2. Update selectors in `scraper.py`
3. Test locally before deploying

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Verify all configuration files

## 📄 License

This project is for educational and personal use only.

## 🙏 Acknowledgments

- Built for monitoring Internshala opportunities
- Uses BeautifulSoup for web scraping
- Gmail SMTP for notifications

---

**Good luck with your internship applications!** 🍀
