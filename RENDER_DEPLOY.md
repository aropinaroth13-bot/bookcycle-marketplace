# Deploy BOOKCYCLE to Render (100% FREE - No Credit Card!) 🚀

Render.com offers completely free hosting with PostgreSQL and Redis - no payment info required!

---

## Step 1: Create GitHub Repository (5 minutes)

Your code needs to be on GitHub first.

### If you don't have GitHub account:
1. Go to https://github.com/signup
2. Create free account
3. Verify your email

### Push your code to GitHub:

```powershell
# Make sure you're in your project
cd C:\Users\Aromal\.gemini\antigravity\scratch\bookcycle

# Add all files
git add .
git commit -m "Ready for Render deployment"

# Create repo on GitHub:
# 1. Go to https://github.com/new
# 2. Name it: bookcycle-marketplace
# 3. Make it Public
# 4. DON'T add README, .gitignore, or license
# 5. Click "Create repository"

# Connect and push (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/bookcycle-marketplace.git
git branch -M main
git push -u origin main
```

---

## Step 2: Sign Up for Render (1 minute)

1. Go to https://render.com/
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest!)
4. Authorize Render to access your repositories
5. Done! ✅

---

## Step 3: Create PostgreSQL Database (2 minutes)

1. From Render Dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Fill in:
   - **Name:** `bookcycle-db`
   - **Database:** `bookcycle`
   - **User:** `bookcycle_user`
   - **Region:** Singapore (closest to India)
   - **Plan:** **FREE** ✅
4. Click **"Create Database"**
5. Wait 1-2 minutes for it to provision
6. **Copy the "Internal Database URL"** - you'll need this!

---

## Step 4: Create Redis Instance (2 minutes)

1. Click **"New +"** again
2. Select **"Redis"**
3. Fill in:
   - **Name:** `bookcycle-redis`
   - **Region:** Singapore
   - **Plan:** **FREE** (25 MB) ✅
4. Click **"Create Redis"**
5. **Copy the "Internal Redis URL"** - you'll need this!

---

## Step 5: Create Web Service (3 minutes)

1. Click **"New +"** again
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Find `bookcycle-marketplace`
   - Click **"Connect"**
4. Fill in settings:
   - **Name:** `bookcycle-marketplace`
   - **Region:** Singapore
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:**
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```
     gunicorn bookcycle.wsgi:application
     ```
   - **Plan:** **Free** ✅

5. Click **"Advanced"** and add these **Environment Variables**:

### Environment Variables to Add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.7` |
| `DATABASE_URL` | *Paste Internal Database URL from Step 3* |
| `REDIS_URL` | *Paste Internal Redis URL from Step 4* |
| `SECRET_KEY` | *Generate below* |
| `ALLOWED_HOSTS` | `bookcycle-marketplace.onrender.com` |
| `DJANGO_SETTINGS_MODULE` | `bookcycle.settings` |

**To generate SECRET_KEY**, run locally:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. Click **"Create Web Service"**

---

## Step 6: Wait for Deployment (3-5 minutes)

Render will:
- Install dependencies
- Run migrations automatically
- Collect static files
- Start your app

Watch the logs in real-time!

---

## Step 7: Run Database Migrations

Once deployed, go to your web service and:

1. Click **"Shell"** tab
2. Run:
   ```bash
   python manage.py migrate
   ```

---

## Step 8: Create Superuser

In the same Shell:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

---

## Step 9: Visit Your Live Site! 🎉

Your site is live at:
```
https://bookcycle-marketplace.onrender.com
```

Click the URL in Render dashboard or visit it directly!

---

## What You Get FREE:

✅ **750 hours/month** of web service (enough for always-on)  
✅ **PostgreSQL database** (1 GB storage)  
✅ **Redis cache** (25 MB)  
✅ **Free SSL certificate** (HTTPS)  
✅ **Custom subdomain**  
✅ **No credit card required!**  
✅ **Auto-deploy on git push**  

---

## Render vs Heroku:

| Feature | Render (Free) | Heroku (Free) |
|---------|---------------|---------------|
| Credit card required? | ❌ NO | ✅ YES |
| PostgreSQL | ✅ 1 GB | ✅ 10K rows |
| Redis | ✅ 25 MB | ✅ 25 MB |
| Always-on | ✅ 750h/month | ⚠️ Sleeps after 30min |
| SSL | ✅ Free | ✅ Free |
| Auto-deploy | ✅ Yes | ✅ Yes |

---

## Auto-Deploy on Updates

Every time you push to GitHub:

```powershell
git add .
git commit -m "Update description"
git push origin main
```

Render **automatically redeploys**! 🎊

---

## Troubleshooting

### Check Logs
Click **"Logs"** tab in your web service to see errors.

### Common Issues:

**"Application Error"**
- Check environment variables are set correctly
- Verify DATABASE_URL and REDIS_URL are the **Internal** URLs

**Static files not loading**
- Make sure build command includes `collectstatic`
- Check `STATIC_ROOT` in settings.py

**Database connection error**
- Use the **Internal Database URL**, not External
- Make sure migrations ran: run `python manage.py migrate` in Shell

---

## Optional: Configure Email

Once deployed, add email settings:

1. Go to your web service
2. Click **"Environment"** tab
3. Add:
   - `EMAIL_HOST_USER` = your-email@gmail.com
   - `EMAIL_HOST_PASSWORD` = your-app-password
   - `DEFAULT_FROM_EMAIL` = BOOKCYCLE <noreply@yourdomain.com>

---

## Optional: Custom Domain (Later)

1. Buy a domain (GoDaddy, Namecheap, etc.)
2. In Render, go to web service settings
3. Click **"Custom Domains"**
4. Add your domain
5. Update DNS records as shown
6. Free SSL certificate automatically issued!

---

## Need Help?

- **Render Docs:** https://render.com/docs
- **Django on Render:** https://render.com/docs/deploy-django
- **Check Logs:** Click "Logs" tab in dashboard

---

**Congratulations! Your marketplace is LIVE on Render!** 🎊

No credit card. Completely free. Professional hosting! 🚀
