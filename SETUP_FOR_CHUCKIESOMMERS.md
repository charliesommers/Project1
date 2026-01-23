# Setup Guide for chuckiesommers@gmail.com

## 📧 Email Automation Setup

To get picks emailed to **chuckiesommers@gmail.com** daily at **5:30 AM Central Time**:

---

## Step 1: Get Gmail App Password

1. **Go to:** https://myaccount.google.com/apppasswords
2. **Sign in** with chuckiesommers@gmail.com
3. **Select app:** Mail
4. **Select device:** Other (Custom name) → Type "CBB Picker"
5. **Click Generate**
6. **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)

---

## Step 2: Update .env File

Edit `/home/user/Project1/.env` and add these lines:

```bash
# API Configuration (already there)
ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602

# Email Configuration (ADD THESE)
EMAIL_FROM=chuckiesommers@gmail.com
EMAIL_TO=chuckiesommers@gmail.com
EMAIL_PASSWORD=your_16_char_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Replace `your_16_char_app_password_here` with the password from Step 1**

---

## Step 3: Test Email

Run this command to test:

```bash
cd /home/user/Project1
python3 email_picks.py chuckiesommers@gmail.com
```

You should receive an email with today's picks!

---

## Step 4: Set Up Daily Automation (5:30 AM Central)

### Option A: Use Setup Script (Easiest)

```bash
bash setup_automation.sh
```

- Choose option 1 (CST - Winter) for November-March
- Choose option 2 (CDT - Summer) for March-November

### Option B: Manual Setup

```bash
# Create logs folder
mkdir -p /home/user/Project1/logs

# Open crontab
crontab -e

# Add this line (for winter CST - 5:30 AM Central = 11:30 AM UTC)
30 11 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1

# Save and exit (Ctrl+X, then Y, then Enter)
```

**For summer (March-November), use:**
```bash
30 10 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1
```

---

## Step 5: Verify Cron Job

```bash
# Check cron is set up
crontab -l

# View email logs later
tail -f /home/user/Project1/logs/email.log
```

---

## ✅ Done!

Every day at **5:30 AM Central Time**, you'll receive an email like this:

**Subject:** CBB Picks - January 23, 2026

**Body:**
```
📅 January 23, 2026 - CBB TOTALS PICKS

🔥 ⬇️ UNDER 145.5 - Purdue vs Indiana
   Edge: 7.0 pts | Greg: 138.5 | Book: 145.5

🔥 ⬆️ OVER 150.0 - Gonzaga vs Saint Marys
   Edge: 6.5 pts | Greg: 156.5 | Book: 150.0

────────────────────────────────────────────────
⬇️ = Under | ⬆️ = Over
🔥 = High confidence | ✓ = Good bet
────────────────────────────────────────────────
```

**Just check your email on your iPad!** 📱📧🏀

---

## 🔧 Troubleshooting

**Email not sending?**
```bash
# Check .env has all fields
cat /home/user/Project1/.env

# Test manually
python3 email_picks.py chuckiesommers@gmail.com
```

**Cron not running?**
```bash
# Check cron job exists
crontab -l

# Check logs
tail /home/user/Project1/logs/email.log

# Restart cron service
sudo systemctl restart cron
```

**App password not working?**
- Make sure 2-Factor Authentication is enabled on Gmail
- Remove any spaces from the 16-character password
- Try generating a new app password

---

## 📞 Quick Reference

**Your email:** chuckiesommers@gmail.com
**Time:** 5:30 AM Central Time
**Cron time (Winter):** 11:30 AM UTC → `30 11 * * *`
**Cron time (Summer):** 10:30 AM UTC → `30 10 * * *`

**Test command:**
```bash
python3 email_picks.py chuckiesommers@gmail.com
```

**Setup command:**
```bash
bash setup_automation.sh
```

---

See [sample_email.txt](sample_email.txt) for what the email will look like!
