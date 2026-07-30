# 🔬 Research Paper Agent

> **Auto-fetch daily new papers** from arXiv on **Medical Images + Deep Learning** and get them delivered to your **email inbox** every morning.

---

## 📁 Files in this Repo

| File | Purpose |
|------|---------|
| `agent.py` | Main Python script — fetches papers & sends email |
| `.github/workflows/daily-papers.yml` | GitHub Actions — runs daily at 9 AM UTC |
| `requirements.txt` | Dependencies (empty — uses stdlib only) |
| `sent_papers.json` | Tracks which papers were already sent (auto-created) |

---

## 🚀 Step-by-Step Setup (Complete Guide)

### Step 1: Create the GitHub Repo

1. Go to [github.com/new](https://github.com/new)
2. **Repository name:** `research-paper-agent`
3. **Visibility:** Public (or Private — both work)
4. **Do NOT** initialize with README (we'll push our own)
5. Click **Create repository**

---

### Step 2: Push Code to GitHub

Open terminal / command prompt and run these commands:

```bash
# 1. Go to the folder where you downloaded these files
cd research-paper-agent

# 2. Initialize git
git init

# 3. Add all files
git add .

# 4. Commit
git commit -m "Initial commit: Research Paper Agent"

# 5. Add your repo as remote (replace with your actual URL)
git remote add origin https://github.com/ahsanfiaz15/research-paper-agent.git

# 6. Push to main branch
git branch -M main
git push -u origin main
```

---

### Step 3: Add GitHub Secrets (Very Important!)

These secrets store your email credentials **safely** — they are encrypted and never shown publicly.

1. Go to your repo on GitHub
2. Click **Settings** tab → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `EMAIL_SENDER` | `ahsan.firebase15@gmail.com` |
| `EMAIL_PASSWORD` | `olvq jmzs ezly pdpu` |
| `EMAIL_RECIPIENT` | `ahsan.firebase15@gmail.com` |

> 💡 **Note:** `EMAIL_PASSWORD` mein wohi App Password daalna jo aapne diya hai. Spaces hain toh waisay hi rakhna.

---

### Step 4: Test It Manually (Right Now!)

1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **Daily Research Paper Agent** (left sidebar)
4. Click **Run workflow** → **Run workflow** (green button)
5. Wait 1-2 minutes
6. Check your Gmail inbox — you should receive the first email!

---

### Step 5: It Runs Automatically Every Day! 🎉

The workflow is set to run **daily at 9:00 AM UTC** (which is **2:00 PM Pakistan Time**).

If you want to change the time, edit this line in `.github/workflows/daily-papers.yml`:

```yaml
- cron: '0 9 * * *'   # 9 AM UTC = 2 PM PKT
```

**Cron format:** `minute hour day-of-month month day-of-week`

Examples:
- `0 6 * * *` = 6 AM UTC (11 AM PKT)
- `0 12 * * *` = 12 PM UTC (5 PM PKT)
- `0 9 * * 1` = Every Monday 9 AM UTC

---

## 🔧 How It Works

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  GitHub Actions │────▶│  arXiv API  │────▶│  Filter     │
│  (Daily 9 AM)   │     │  (Papers)     │     │  Medical+DL │
└─────────────────┘     └─────────────┘     └──────┬──────┘
                                                    │
                              ┌─────────────────────┘
                              ▼
                       ┌─────────────┐
                       │  Gmail SMTP │
                       │  (Email)    │
                       └──────┬──────┘
                              ▼
                       ┌─────────────┐
                       │ Your Inbox  │
                       └─────────────┘
```

---

## 🛠️ Customization

### Change Search Keywords

Edit `agent.py` — look for `KEYWORDS` list:

```python
KEYWORDS = ["medical", "clinical", "radiology", "mri", "ct scan", ...]
```

Add/remove keywords as you like.

### Change Paper Source

Currently uses **arXiv** (free, no API key). You can also add:
- **PubMed** (medical focus)
- **bioRxiv** (biology preprints)
- **medRxiv** (medical preprints)

Just add another function like `fetch_pubmed_papers()` and merge results.

### Change Email Design

The HTML email template is inside `send_email()` function in `agent.py`. Edit the CSS/styles there.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| Email not received | Check Gmail Spam folder. Also verify `EMAIL_PASSWORD` is correct App Password (not regular password). |
| Workflow fails | Go to **Actions** tab → click failed run → read error logs. Usually it's a secret name typo. |
| No papers found | arXiv might not have new papers in last 24h. Agent will send "No new papers today" email. |
| `git push` fails | Make sure you created the empty repo on GitHub first, or use `git push -f origin main` |

---

## 📬 About the Gmail App Password

The password `olvq jmzs ezly pdpu` is a **Gmail App Password** (16 characters, spaces). It works without 2FA issues. If it ever stops working:

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Generate a new App Password for "Mail"
3. Update the `EMAIL_PASSWORD` secret in GitHub

---

## 📜 License

MIT — free to use and modify.

---

**Built with ❤️ for researchers who hate missing new papers!**
