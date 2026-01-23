# Start Here - Get Daily Picks on Your iPad

## ✅ What's Set Up

Your CBB picks system is complete! Here's what you have:

1. ✅ **API Key configured** (in `.env`)
2. ✅ **Picks scripts ready** (with down/up arrows ⬇️⬆️)
3. ✅ **Automation scripts** (for 5:30 AM Central Time)
4. ✅ **Demo available** (try it now!)

---

## 🎯 Try It Now (See the Demo)

```bash
python demo_picks.py
```

**You'll see:**
```
📅 January 23, 2026 - CBB TOTALS PICKS

🔥 ⬇️ UNDER 145.5 - Purdue vs Indiana
   Edge: 7.0 pts | Greg: 138.5 | Book: 145.5

🔥 ⬆️ OVER 150.0 - Gonzaga vs Saint Marys
   Edge: 6.5 pts | Greg: 156.5 | Book: 150.0

────────────────────────────────────────────────
🔥 = High confidence | ✓ = Good bet
⬇️ = Under | ⬆️ = Over
────────────────────────────────────────────────
```

---

## 📧 Set Up Automation (5:30 AM Central Time)

### Quick Setup (2 minutes):

```bash
bash setup_automation.sh
```

The script will:
1. Check your email config
2. Let you test email
3. Set up daily automation at 5:30 AM Central Time
4. Handle timezone automatically (CST/CDT)

### Manual Setup:

**1. Add email to `.env`:**
```bash
EMAIL_FROM=your@gmail.com
EMAIL_TO=your@gmail.com
EMAIL_PASSWORD=your_app_password
```

**2. Get Gmail App Password:**
- Go to: https://myaccount.google.com/apppasswords
- Create password for "Mail"
- Copy 16-character code
- Use as `EMAIL_PASSWORD`

**3. Set up cron job:**
```bash
# Open crontab
crontab -e

# Add this line (for winter CST)
30 11 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1

# Save and exit
```

**4. Create logs folder:**
```bash
mkdir -p /home/user/Project1/logs
```

---

## 📱 How to Check on iPad

### Email Method (Easiest):
1. Open **Mail app** on iPad
2. Check at 5:30 AM Central Time
3. Read your picks!

### File Method (Alternative):
If you prefer file sync instead of email:

```bash
# Set up file saving to Dropbox
crontab -e

# Add (for Dropbox sync)
30 11 * * * cd /home/user/Project1 && /usr/bin/python3 save_picks_daily.py ~/Dropbox/CBB_Picks >> /home/user/Project1/logs/save.log 2>&1
```

Then on iPad:
1. Open **Dropbox app**
2. Go to **CBB_Picks** folder
3. Open **latest.txt**

---

## 🕐 Timezone Info

**5:30 AM Central Time converts to:**
- **Winter (Nov-Mar)**: 11:30 AM UTC → Use `30 11 * * *`
- **Summer (Mar-Nov)**: 10:30 AM UTC → Use `30 10 * * *`

**The `setup_automation.sh` script handles this for you!**

When daylight saving time changes, just run the script again and select the new timezone.

---

## ⬇️⬆️ New Emoji Symbols

- **⬇️ = UNDER** (Greg's total is below sportsbook)
- **⬆️ = OVER** (Greg's total is above sportsbook)
- **🔥 = High confidence** (large edge)
- **✓ = Good bet** (meets minimum criteria)

---

## 📚 Full Documentation

- **[QUICK_AUTOMATION.md](QUICK_AUTOMATION.md)** - 5-minute setup
- **[AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)** - Complete guide
- **[HOW_TO_GET_PICKS.md](HOW_TO_GET_PICKS.md)** - All pick methods
- **[YOUR_SETUP_GUIDE.md](YOUR_SETUP_GUIDE.md)** - Personal guide
- **[CBB_PICKER_README.md](CBB_PICKER_README.md)** - Full docs

---

## ⚡ Quick Commands

**See demo:**
```bash
python demo_picks.py
```

**Test email:**
```bash
python email_picks.py your@email.com
```

**Run automation setup:**
```bash
bash setup_automation.sh
```

**Check cron jobs:**
```bash
crontab -l
```

**View logs:**
```bash
tail -f logs/email.log
```

---

## 🎲 Your Strategy

✅ **Bet UNDER** when Greg's total is ≥5 points BELOW Bet365
✅ **Bet OVER** when Greg's total is ≥3 points ABOVE Bet365

---

## ✨ Next Steps

1. **Try demo**: `python demo_picks.py`
2. **Set up automation**: `bash setup_automation.sh`
3. **Check iPad** tomorrow at 5:30 AM for your picks!

---

## 🆘 Need Help?

**Email not sending?**
- Check `.env` has EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD
- Test: `python email_picks.py`

**Cron not running?**
- Check: `crontab -l`
- View log: `tail logs/email.log`

**API issues?**
- Verify `.env` has: `ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602`

---

## 🏀 You're All Set!

Run `bash setup_automation.sh` to get started, and you'll receive picks on your iPad every day at 5:30 AM Central Time!

Good luck! 🎲
