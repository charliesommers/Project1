# GitHub Actions Quick Start (iPad)

**Get daily picks with ZERO cost - all from your iPad!**

## 📱 Setup in 5 Minutes

### Step 1: Get Gmail App Password

**On iPad Safari:**

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in: **chuckiesommers@gmail.com**
3. **Select app:** Mail
4. **Select device:** Other → Type "GitHub Actions"
5. Click **Generate**
6. **Copy password** (16 characters like: `abcd efgh ijkl mnop`)
7. **Remove spaces** → `abcdefghijklmnop`

✅ **Save this password** - you'll need it in Step 3

---

### Step 2: Push Code to GitHub

The code is already in repository: `charliesommers/Project1`

If you need to create the repo:
1. Go to **GitHub.com** on iPad
2. Click **New repository**
3. Name: `CBB-Picks`
4. Push this code (someone with a computer can help, or use GitHub's web upload)

---

### Step 3: Add Secrets to GitHub

**On iPad Safari at GitHub.com:**

1. Go to your repository: `charliesommers/Project1`
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret** (green button)

**Add these 4 secrets (one at a time):**

#### Secret 1:
- **Name:** `ODDS_API_KEY`
- **Secret:** `32a952b95065c6b8c74f1e72ac125602`
- Click **Add secret**

#### Secret 2:
- **Name:** `EMAIL_FROM`
- **Secret:** `chuckiesommers@gmail.com`
- Click **Add secret**

#### Secret 3:
- **Name:** `EMAIL_TO`
- **Secret:** `chuckiesommers@gmail.com`
- Click **Add secret**

#### Secret 4:
- **Name:** `EMAIL_PASSWORD`
- **Secret:** [Paste your Gmail app password from Step 1]
- Click **Add secret**

---

### Step 4: Enable GitHub Actions

**In your repository:**

1. Click **Actions** tab (top menu)
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see **"Daily CBB Picks Email"** in the list

---

### Step 5: Test It Now!

**Don't wait until tomorrow - test immediately:**

1. Stay in **Actions** tab
2. Click **"Daily CBB Picks Email"** (left sidebar)
3. Click **Run workflow** (blue button on right)
4. Click **Run workflow** again (green button in popup)

**Wait 1-2 minutes, then check your email!** 📧

You should receive picks email at **chuckiesommers@gmail.com**

---

## ✅ You're Done!

**What happens now:**

- **Every day at 5:30 AM Central Time**, GitHub automatically:
  1. Fetches Greg's lines from VSIN
  2. Gets Bet365 odds
  3. Generates picks
  4. Emails you at chuckiesommers@gmail.com

**Cost: $0** (completely free!)

---

## 📱 Using It from iPad

### Check if it ran:
1. Open Safari → GitHub.com → Your repo
2. Click **Actions**
3. See recent runs with ✅ or ❌

### Run it manually anytime:
1. **Actions** → **Daily CBB Picks Email**
2. Click **Run workflow**

### View what it sent:
1. **Actions** → Click on a run
2. Click **send-picks** job
3. Expand **Send picks email** step
4. See output/errors

---

## 🕐 Time Schedule

**Current:** 5:30 AM Central (Winter)
- Runs at **11:30 AM UTC**
- Cron: `30 11 * * *`

**To change time:**
1. Go to repository on GitHub
2. Click `.github/workflows/daily-picks.yml`
3. Click edit (pencil icon)
4. Change `cron: '30 11 * * *'` to different time
5. Commit changes

**Time converter:**
- 5:30 AM CST = 11:30 AM UTC → `30 11`
- 6:00 AM CST = 12:00 PM UTC → `0 12`
- 7:00 AM CST = 1:00 PM UTC → `0 13`

---

## 🔧 Troubleshooting

### Email not arriving?

**Check workflow ran:**
1. **Actions** → Click latest run
2. Look for ✅ (success) or ❌ (failed)

**If failed, check logs:**
1. Click the failed run
2. Click **send-picks**
3. Expand **Send picks email**
4. Read error message

**Common issues:**
- ❌ App password wrong → Re-check Secret 4
- ❌ API key wrong → Re-check Secret 1
- ❌ Gmail credentials → Verify EMAIL_FROM and EMAIL_PASSWORD secrets

**Re-check secrets:**
1. **Settings** → **Secrets and variables** → **Actions**
2. Verify all 4 are there
3. Can't view them, but can delete/recreate if needed

### Need to update secrets?

1. **Settings** → **Secrets and variables** → **Actions**
2. Click secret name
3. Click **Update** (or delete and recreate)

---

## 📧 What You'll Receive

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
🔥 = High confidence
```

---

## 💡 Pro Tips

**Test before game day:**
- Run workflow manually to verify it works
- Check email arrives correctly

**Check logs occasionally:**
- Make sure it's running daily
- See if any errors

**Adjust thresholds:**
- Edit `email_picks.py` on GitHub
- Change `under_threshold=5.0` or `over_threshold=3.0`

**Multiple emails:**
- Can add multiple email addresses to EMAIL_TO
- Separate with commas: `email1@gmail.com,email2@gmail.com`

---

## ✨ Summary

1. **Get Gmail app password** → https://myaccount.google.com/apppasswords
2. **Add 4 secrets** → Settings → Secrets → Actions
3. **Test it** → Actions → Run workflow
4. **Done!** → Emails arrive daily at 5:30 AM Central

**All from your iPad. Zero cost. Forever.** 🎉🏀

Questions? Check the workflow logs in the Actions tab!
