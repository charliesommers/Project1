# iPad-Only Setup Guide

No computer needed! Get daily picks emailed to your iPad.

## 🌟 Option 1: GitHub Actions (100% FREE - Recommended)

GitHub will run the code in the cloud and email you picks daily!

### Step 1: Set Up GitHub Repository

**On your iPad (using Safari):**

1. Go to **GitHub.com** and sign in (or create account)
2. This code is already in a repository
3. You just need to add your email credentials as "Secrets"

### Step 2: Add Secrets to GitHub

**In your repository on GitHub.com:**

1. Go to **Settings** (top menu)
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these 4 secrets one by one:

**Secret 1:**
- Name: `ODDS_API_KEY`
- Value: `32a952b95065c6b8c74f1e72ac125602`

**Secret 2:**
- Name: `EMAIL_FROM`
- Value: `chuckiesommers@gmail.com`

**Secret 3:**
- Name: `EMAIL_TO`
- Value: `chuckiesommers@gmail.com`

**Secret 4:**
- Name: `EMAIL_PASSWORD`
- Value: Your Gmail app password (see below)

### Step 3: Get Gmail App Password

**On iPad Safari:**

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in with **chuckiesommers@gmail.com**
3. Click **Select app** → Choose **Mail**
4. Click **Select device** → Choose **Other** → Type "GitHub Actions"
5. Click **Generate**
6. **Copy the 16-character password** (remove spaces)
7. Use this as `EMAIL_PASSWORD` secret in GitHub

### Step 4: Enable GitHub Actions

**In your repository:**

1. Go to **Actions** tab
2. Click **Enable workflows**
3. Find **"Daily CBB Picks Email"**
4. Click **Run workflow** to test immediately

### Step 5: Verify

- Check your email (chuckiesommers@gmail.com)
- Should receive picks within 1-2 minutes!
- After that, runs automatically every day at 5:30 AM Central

### ✅ Done!

**From your iPad, you can:**
- Trigger manually: **Actions** → **Daily CBB Picks Email** → **Run workflow**
- View logs: **Actions** → Click on any run
- Change schedule: Edit `.github/workflows/daily-picks.yml`

**Cost: FREE** (GitHub Actions is free for public repos)

---

## 🌐 Option 2: Replit (Browser-Based)

**Run Python in your browser - works on iPad!**

### Step 1: Set Up Replit

1. Go to **https://replit.com** on Safari
2. Sign up (free account)
3. Click **Create Repl**
4. Choose **Python** template
5. Name it "CBB-Picks"

### Step 2: Upload Files

1. In Replit, click **Files** icon (left sidebar)
2. Upload all `.py` files from this project
3. Upload `requirements.txt`

### Step 3: Create .env File

In Replit, create file `.env` with:

```bash
ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602
EMAIL_FROM=chuckiesommers@gmail.com
EMAIL_TO=chuckiesommers@gmail.com
EMAIL_PASSWORD=your_gmail_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Step 4: Install Dependencies

In Replit **Shell** (bottom), run:
```bash
pip install -r requirements.txt
```

### Step 5: Test It

In Shell, run:
```bash
python email_picks.py
```

Check your email!

### Step 6: Schedule Daily

**Replit's Always-On (requires Paid plan - $7/month):**
- Or manually run daily from iPad

**Free alternative:**
- Use **UptimeRobot** to ping your Repl every day
- Add a simple web endpoint to trigger the email

---

## 💰 Option 3: Cheap VPS ($5/month)

**Like having a computer in the cloud - access via iPad SSH app**

### Step 1: Get a VPS

Choose one:
- **DigitalOcean** ($6/month)
- **Linode** ($5/month)
- **Vultr** ($6/month)

### Step 2: Access from iPad

Install **Termius** app (free SSH client for iPad):
1. Download **Termius** from App Store
2. Add your VPS connection
3. SSH in from iPad

### Step 3: Set Up Code

```bash
# On VPS via Termius
git clone [your-repo-url]
cd Project1
pip install -r requirements.txt

# Add .env file with email credentials
nano .env

# Test
python email_picks.py

# Set up cron
crontab -e
# Add: 30 11 * * * cd /home/user/Project1 && python3 email_picks.py
```

**Cost: ~$5-6/month**

---

## 🎯 Recommended: GitHub Actions

**Why GitHub Actions is best:**
- ✅ **100% FREE**
- ✅ **No maintenance**
- ✅ **Reliable**
- ✅ **Works from iPad Safari**
- ✅ **Can trigger manually anytime**
- ✅ **View logs easily**

**Setup time: 5 minutes**

---

## 📧 Testing from iPad

**GitHub Actions:**
- Go to Actions tab → Click workflow → Run manually

**Replit:**
- Open Shell → Type `python email_picks.py`

**VPS:**
- Open Termius → SSH in → Run `python email_picks.py`

---

## 🔧 Troubleshooting

**Email not sending?**
- Check GitHub Secrets are set correctly
- Verify Gmail app password (no spaces)
- Check workflow logs in Actions tab

**Workflow not running?**
- Check it's enabled in Actions tab
- Verify cron schedule (11:30 UTC = 5:30 CST winter)
- Can trigger manually to test

**Need different time?**
- Edit `.github/workflows/daily-picks.yml`
- Change `cron: '30 11 * * *'` to desired UTC time

---

## 💡 Quick Start (GitHub Actions)

1. **Add 4 secrets** to GitHub repo (Settings → Secrets → Actions):
   - `ODDS_API_KEY`: 32a952b95065c6b8c74f1e72ac125602
   - `EMAIL_FROM`: chuckiesommers@gmail.com
   - `EMAIL_TO`: chuckiesommers@gmail.com
   - `EMAIL_PASSWORD`: [your Gmail app password]

2. **Enable Actions** (Actions tab → Enable)

3. **Test it** (Actions → Daily CBB Picks Email → Run workflow)

4. **Done!** Receives email daily at 5:30 AM Central

---

## 📱 Managing from iPad

**All from Safari:**
- Trigger picks: GitHub → Actions → Run workflow
- View logs: GitHub → Actions → Click run
- Edit schedule: GitHub → Edit `.github/workflows/daily-picks.yml`
- Check email: Mail app

**No computer ever needed!** 🎉
