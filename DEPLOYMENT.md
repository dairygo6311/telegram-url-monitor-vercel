# Vercel Par Deploy Karne Ka Tarika

## Step 1: Vercel Account Banao
1. [vercel.com](https://vercel.com) par jaao
2. GitHub account se sign up karo

## Step 2: Code Upload Karo
Sirf `vercel-deploy` folder ka content deploy karna hai.

### Option A: GitHub se (Recommended)
1. Sirf `vercel-deploy` folder ka content ek naye GitHub repo mein daalo
2. Vercel dashboard mein "New Project" click karo
3. Apna GitHub repo select karo
4. Deploy click karo

### Option B: Vercel CLI se
```bash
# vercel-deploy folder mein jaao
cd vercel-deploy

# Vercel CLI install karo
npm i -g vercel

# Deploy karo
vercel
```

## Step 3: Environment Variables Set Karo
Vercel Dashboard → Your Project → Settings → Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `BOT_TOKEN` | `8405898835:AAE...` | Aapka Telegram Bot Token |
| `ADMIN_CHAT_ID` | `1691680798` | Aapka Telegram Chat ID |

## Step 4: Webhook Register Karo (ZAROORI)
Deploy hone ke baad, apna bot ka webhook register karna padega:

1. Browser mein kholo: `https://your-app.vercel.app/api/setup`
2. Apna Vercel domain enter karo (example: `my-bot.vercel.app`)
3. "Register Webhook" click karo
4. "success" message aaye toh kaam ho gaya!

## Step 5: Test Karo
1. Telegram mein apne bot par jaao
2. `/start` command bhejo
3. Bot reply kare toh sab theek hai!

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

## Important Notes

### Data Persistence
- Vercel ke `/tmp` folder mein data store hota hai
- **Data deployments ke beech delete ho sakta hai** (Vercel serverless limitation)
- Permanent data ke liye Vercel KV ya koi external database use karo

### URL Monitoring
- Monitoring Vercel Cron Job ke through har minute hoti hai
- Vercel Free Plan mein 2 cron jobs allowed hain
- Agar cron kaam na kare, manually `/api/monitor` URL call kar sakte ho

### Web Page
- `https://your-app.vercel.app/` - Bot ka welcome page
- `https://your-app.vercel.app/api/status` - Status check
- `https://your-app.vercel.app/api/monitor` - Manual monitoring trigger
- `https://your-app.vercel.app/api/setup` - Webhook setup

---

## Folder Structure
```
vercel-deploy/
├── api/
│   ├── webhook.py      ← Telegram se updates receive karta hai
│   ├── monitor.py      ← Cron job se URLs ping karta hai
│   ├── index.py        ← Web page serve karta hai
│   └── setup_webhook.py ← Webhook register karne ka tool
├── config.py
├── bot_handlers.py
├── url_monitor.py
├── data_manager.py
├── utils.py
├── advanced_ui.py
├── future_features.py
├── vercel.json         ← Vercel configuration
├── requirements.txt    ← Python packages
└── DEPLOYMENT.md       ← Yahi file
```
