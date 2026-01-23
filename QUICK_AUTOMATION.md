# Quick Automation Setup (5 Minutes)

Get picks emailed to your iPad daily!

## ⚡ Super Fast Setup

### 1. Add Email to .env File

Edit `/home/user/Project1/.env` and add:

```bash
EMAIL_FROM=your@gmail.com
EMAIL_TO=your@gmail.com
EMAIL_PASSWORD=your_app_password
```

**Get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Create password for "Mail" on "Other device"
3. Copy the 16-character password
4. Paste as EMAIL_PASSWORD (no spaces)

### 2. Test It

```bash
cd /home/user/Project1
python email_picks.py
```

You should get an email with picks!

### 3. Set Up Daily Automation

```bash
# Open crontab
crontab -e

# Add this line (sends email at 10 AM daily)
0 10 * * * cd /home/user/Project1 && python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1

# Save and exit
```

### 4. Create Logs Folder

```bash
mkdir -p /home/user/Project1/logs
```

## ✅ Done!

You'll now get picks emailed every day at 10 AM.

**Check on iPad**: Just open your email! 📧🏀

---

## Alternative: Save to File Instead

If you prefer saving to Dropbox/iCloud instead of email:

```bash
# In crontab, use this instead:
0 10 * * * cd /home/user/Project1 && python3 save_picks_daily.py ~/Dropbox/CBB_Picks >> /home/user/Project1/logs/save.log 2>&1
```

Then access `~/Dropbox/CBB_Picks/latest.txt` from iPad!

---

## Change Time

Edit the crontab line:

```bash
# 8 AM
0 8 * * * [command]

# 9:30 AM
30 9 * * * [command]

# 11 AM
0 11 * * * [command]
```

---

## Troubleshooting

**Email not sending?**
- Check .env has EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD
- Test: `python email_picks.py`

**Cron not running?**
- Check: `crontab -l`
- View log: `tail logs/email.log`

---

See **[AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)** for complete details!
