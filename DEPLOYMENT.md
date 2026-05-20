# Vercel Par Deploy Karne Ka Tarika

## Step 1: Vercel Account Banao
1. [vercel.com](https://vercel.com) par jaao
2. GitHub account se sign up karo

## Step 2: GitHub Repo Import Karo
1. Vercel dashboard mein "Add New Project" click karo
2. `telegram-url-monitor-vercel` repo select karo
3. **Deploy** click karo

## Step 3: Environment Variables Set Karo
Vercel Dashboard → Your Project → Settings → Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `BOT_TOKEN` | `8405898835:AAE...` | Aapka Telegram Bot Token |
| `ADMIN_CHAT_ID` | `1691680798` | Aapka Telegram Chat ID |

## Step 4: Webhook Register Karo (ZAROORI)
Deploy hone ke baad browser mein kholo:
`https://your-app.vercel.app/api/setup`
- Apna Vercel domain enter karo (example: `my-bot.vercel.app`)
- "Register Webhook" click karo
- "success" aaye toh webhook register ho gaya!

## Step 5: Free URL Monitoring Setup (cron-job.org)

Vercel ka built-in cron free nahi hai, isliye **cron-job.org** use karo — bilkul FREE hai!

### Setup karne ka tarika:
1. [cron-job.org](https://cron-job.org) par free account banao
2. Login karo → "CREATE CRONJOB" click karo
3. Yeh settings karo:
   - **Title:** `Telegram Bot Monitor`
   - **URL:** `https://your-app.vercel.app/api/monitor`
   - **Schedule:** `Every 1 minute`
4. Save karo — bas ho gaya!

Ab har minute automatically saari URLs ping hongi aur agar koi URL down ho toh Telegram par alert aayega.

---

## Bot Commands
| Command | Description |
|---------|-------------|
| `/start` | Bot start karo |
| `/seturl <url>` | URL monitoring mein add karo |
| `/removeurl <url>` | URL remove karo |
| `/listurls` | Saari URLs dekho |
| `/status` | Stats dekho |
| `/pingnow` | Abhi ping karo |
| `/addadmin <id>` | Admin add karo (primary admin only) |
| `/removeadmin <id>` | Admin remove karo (primary admin only) |
| `/listadmins` | Admins ki list dekho (primary admin only) |

---

## Useful Links
- **Home Page:** `https://your-app.vercel.app/`
- **Webhook Setup:** `https://your-app.vercel.app/api/setup`
- **Manual Monitor Trigger:** `https://your-app.vercel.app/api/monitor`
- **Health Check:** `https://your-app.vercel.app/health`

---

## Important Note: Data Persistence
Vercel serverless mein data `/tmp` folder mein store hota hai.
Restarts pe data reset ho sakta hai — agar permanent storage chahiye toh
Vercel KV ya koi external database (MongoDB Atlas free tier) use karo.

---

## Folder Structure
```
vercel-deploy/
├── api/
│   ├── webhook.py       ← Telegram se updates receive karta hai
│   ├── monitor.py       ← URLs ping karta hai (cron-job.org se trigger)
│   ├── index.py         ← Web page serve karta hai
│   └── setup_webhook.py ← Webhook register karne ka tool
├── config.py
├── bot_handlers.py
├── url_monitor.py
├── data_manager.py
├── utils.py
├── advanced_ui.py
├── future_features.py
├── vercel.json          ← Vercel configuration (no paid cron)
├── requirements.txt
└── DEPLOYMENT.md        ← Yahi file
```
