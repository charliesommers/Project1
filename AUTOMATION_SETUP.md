# Automation Setup Guide

Set up automated daily picks delivery so you can check them on your iPad!

## 🎯 Choose Your Method

### ⭐ Method 1: Email (Easiest for iPad)
Picks sent to your email daily - check on iPad anytime

### 📁 Method 2: Save to File
Picks saved to Dropbox/iCloud/Google Drive - access from iPad

### 📲 Method 3: Both
Get email AND file backup

---

## 📧 Method 1: Email Automation

### Step 1: Set Up Email Credentials

Add to your `.env` file:

```bash
# Email configuration
EMAIL_FROM=your@gmail.com
EMAIL_TO=your@email.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**For Gmail (most common):**

1. **Enable 2-Factor Authentication** on your Google account
2. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" (name it "CBB Picker")
   - Copy the 16-character password
   - Use this as `EMAIL_PASSWORD` (no spaces)

**For other email providers:**
- **Outlook/Hotmail**: `smtp.office365.com`, port 587
- **Yahoo**: `smtp.mail.yahoo.com`, port 587
- **Other**: Search "[provider] SMTP settings"

### Step 2: Test Email

```bash
python email_picks.py your@email.com
```

You should receive an email with today's picks!

### Step 3: Set Up Daily Automation

**On Linux/Mac:**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 10 AM)
0 10 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1
```

**On Windows:**

1. Create `send_picks.bat`:
```batch
@echo off
cd C:\path\to\Project1
python email_picks.py
```

2. Open Task Scheduler
3. Create Basic Task → Daily → 10:00 AM
4. Action: Start a program → `send_picks.bat`

### Step 4: Create Logs Directory

```bash
mkdir -p /home/user/Project1/logs
```

---

## 📁 Method 2: Save to Synced Folder

Perfect if you use Dropbox, iCloud Drive, or Google Drive!

### Step 1: Find Your Sync Folder

**Dropbox:**
```bash
~/Dropbox/
```

**iCloud Drive (Mac):**
```bash
~/Library/Mobile Documents/com~apple~CloudDocs/
```

**Google Drive:**
```bash
~/Google Drive/
```

### Step 2: Test Saving

```bash
# Save to Dropbox example
python save_picks_daily.py ~/Dropbox/CBB_Picks

# Or default location (daily_picks folder)
python save_picks_daily.py
```

Creates:
- `picks_20260123.txt` (dated file)
- `latest.txt` (always current)

### Step 3: Set Up Daily Automation

**On Linux/Mac:**

```bash
crontab -e

# Add this line (change path to your sync folder)
0 10 * * * cd /home/user/Project1 && /usr/bin/python3 save_picks_daily.py ~/Dropbox/CBB_Picks >> /home/user/Project1/logs/save.log 2>&1
```

**On Windows:**

1. Create `save_picks.bat`:
```batch
@echo off
cd C:\path\to\Project1
python save_picks_daily.py "C:\Users\YourName\Dropbox\CBB_Picks"
```

2. Task Scheduler → Daily → 10:00 AM → Run `save_picks.bat`

### Step 4: Access on iPad

1. Install Dropbox/iCloud/Drive app on iPad
2. Navigate to CBB_Picks folder
3. Open `latest.txt` to see today's picks

---

## 📲 Method 3: Both Email AND File

Best of both worlds!

**Cron job (Linux/Mac):**
```bash
0 10 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1 && /usr/bin/python3 save_picks_daily.py ~/Dropbox/CBB_Picks >> /home/user/Project1/logs/save.log 2>&1
```

**Windows batch file:**
```batch
@echo off
cd C:\path\to\Project1
python email_picks.py
python save_picks_daily.py "C:\Users\YourName\Dropbox\CBB_Picks"
```

---

## 🕐 Scheduling Options

### Different Times

```bash
# 8 AM
0 8 * * * [command]

# 9:30 AM
30 9 * * * [command]

# 11 AM
0 11 * * * [command]

# Multiple times (8 AM and 6 PM)
0 8,18 * * * [command]
```

### Only on Weekdays (Mon-Fri)

```bash
0 10 * * 1-5 [command]
```

### Only on Game Days (every day during season)

```bash
0 10 * * * [command]
```

---

## ✅ Verification

### Check if Cron Job is Set

```bash
crontab -l
```

### View Logs

```bash
# Email log
tail -f /home/user/Project1/logs/email.log

# Save log
tail -f /home/user/Project1/logs/save.log
```

### Test Manually

```bash
# Email test
python email_picks.py your@email.com

# File save test
python save_picks_daily.py

# See what was saved
cat daily_picks/latest.txt
```

---

## 🔧 Troubleshooting

### Email Not Sending

**Check .env file:**
```bash
cat .env
```

Should contain:
```
EMAIL_FROM=your@gmail.com
EMAIL_TO=your@email.com
EMAIL_PASSWORD=16-char-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Test email manually:**
```bash
python -c "
import smtplib
from email.message import EmailMessage
msg = EmailMessage()
msg['Subject'] = 'Test'
msg['From'] = 'your@gmail.com'
msg['To'] = 'your@email.com'
msg.set_content('Test email')
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login('your@gmail.com', 'app-password-here')
    smtp.send_message(msg)
print('Email sent!')
"
```

### Cron Job Not Running

**Check cron service:**
```bash
# Status
sudo systemctl status cron

# Restart
sudo systemctl restart cron
```

**Check logs:**
```bash
grep CRON /var/log/syslog
```

### File Not Saving to Sync Folder

**Check permissions:**
```bash
ls -la ~/Dropbox/CBB_Picks
```

**Check path exists:**
```bash
mkdir -p ~/Dropbox/CBB_Picks
```

### API Errors

**Check API key in .env:**
```bash
grep ODDS_API_KEY .env
```

Should show:
```
ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602
```

---

## 📱 Access on iPad

### Email Method
1. Open Mail app
2. Check for daily email
3. Read picks!

### File Method
1. Open Dropbox/iCloud/Drive app
2. Navigate to CBB_Picks folder
3. Open `latest.txt`

### Quick Access
- **Bookmark the folder** in Files app (iPad)
- **Add email to VIP** so you get notifications
- **Use Shortcuts app** to auto-open latest picks

---

## 🎯 Example Complete Setup

### Your .env file:
```bash
# API Key
ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602

# Email settings
EMAIL_FROM=yourgmail@gmail.com
EMAIL_TO=yourgmail@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Your crontab:
```bash
# Email picks daily at 9 AM
0 9 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1

# Also save to Dropbox
5 9 * * * cd /home/user/Project1 && /usr/bin/python3 save_picks_daily.py ~/Dropbox/CBB_Picks >> /home/user/Project1/logs/save.log 2>&1
```

### Result:
- **9:00 AM**: Email arrives with picks
- **9:05 AM**: Dropbox file updated
- **On iPad**: Check email or Dropbox to see picks

---

## 💡 Pro Tips

1. **Test first**: Run manually before automating
2. **Check logs**: Review logs weekly to catch issues
3. **Backup method**: Use both email and file for redundancy
4. **Timing**: Run ~2 hours before first games
5. **Notifications**: Set up email notifications on iPad
6. **Archive**: Files are dated, so you have history

---

## 🆘 Need Help?

**Check these in order:**
1. `.env` file has all credentials
2. Manual run works: `python email_picks.py your@email.com`
3. Cron job is in crontab: `crontab -l`
4. Logs show activity: `tail logs/email.log`
5. API key is valid and has quota

---

## 🎉 Quick Start

**Right now, run this:**

```bash
# 1. Create logs directory
mkdir -p logs

# 2. Test email
python email_picks.py your@email.com

# 3. If that works, set up automation
crontab -e

# 4. Add this line (change email)
0 10 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py your@email.com >> /home/user/Project1/logs/email.log 2>&1

# 5. Done! You'll get picks daily at 10 AM
```

**On iPad**: Just check your email at 10 AM every day! 📧🏀
