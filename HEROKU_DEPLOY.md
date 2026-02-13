# Deploy BOOKCYCLE to Heroku (FREE) 🚀

Follow these steps to deploy your marketplace to Heroku for free!

## Step 1: Create Heroku Account (2 minutes)

1. Go to https://signup.heroku.com/
2. Sign up with your email (no credit card required for free tier)
3. Verify your email
4. Done! ✅

---

## Step 2: Install Heroku CLI (3 minutes)

**Windows:**
1. Download: https://devcenter.heroku.com/articles/heroku-cli
2. Run the installer
3. Restart your terminal/PowerShell

**Verify installation:**
```bash
heroku --version
```

---

## Step 3: Initialize Git (if not already done)

Open terminal in your project folder and run:

```bash
cd C:\Users\Aromal\.gemini\antigravity\scratch\bookcycle

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - BOOKCYCLE marketplace"
```

---

## Step 4: Login to Heroku

```bash
heroku login
```

This will open your browser to login. Login and return to terminal.

---

## Step 5: Create Heroku App

```bash
# Create app (Heroku will generate a random name)
heroku create

# OR create with a specific name (if available)
heroku create bookcycle-marketplace
```

You'll get a URL like: `https://bookcycle-marketplace.herokuapp.com`

---

## Step 6: Add Free PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:essential-0
```

This adds a FREE PostgreSQL database! ✅

---

## Step 7: Add Free Redis Cache

```bash
heroku addons:create heroku-redis:mini
```

This adds FREE Redis caching! ✅

---

## Step 8: Set Environment Variables

```bash
# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy the output and use it below (replace YOUR_SECRET_KEY_HERE)
heroku config:set SECRET_KEY="YOUR_SECRET_KEY_HERE"

# Set Django settings
heroku config:set DJANGO_SETTINGS_MODULE=bookcycle.settings_production
heroku config:set DEBUG=False

# Get your app URL
heroku info
# Copy the "Web URL" and use it below (without https://)

heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"

# Optional: Email settings (can add later)
# heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
# heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
```

---

## Step 9: Deploy! 🚀

```bash
git push heroku main
```

If your branch is named "master":
```bash
git push heroku master
```

**This will:**
- Upload your code
- Install dependencies
- Run migrations automatically
- Start the server

⏱️ Takes 2-3 minutes...

---

## Step 10: Create Superuser

```bash
heroku run python manage.py createsuperuser
```

Follow prompts to create your admin account.

---

## Step 11: Open Your Live Site! 🎉

```bash
heroku open
```

Your marketplace is now LIVE at: `https://your-app-name.herokuapp.com`

---

## Verify Everything Works

1. ✅ Visit your site - should load
2. ✅ Register a new user
3. ✅ Login
4. ✅ List a book
5. ✅ Browse books
6. ✅ Add to cart

---

## Useful Heroku Commands

### View logs (if something goes wrong)
```bash
heroku logs --tail
```

### Run Django commands
```bash
heroku run python manage.py <command>
```

### Open admin panel
```bash
heroku open /admin
```

### Check database
```bash
heroku pg:info
```

### Check Redis
```bash
heroku redis:info
```

### Restart app
```bash
heroku restart
```

---

## Troubleshooting

### Issue: "No web processes running"
```bash
heroku ps:scale web=1
```

### Issue: Database errors
```bash
heroku run python manage.py migrate
```

### Issue: Static files not loading
```bash
heroku run python manage.py collectstatic --noinput
```

### Issue: Check config
```bash
heroku config
```

---

## What You Get FREE:

✅ **Live website** with SSL (HTTPS)  
✅ **PostgreSQL database** (10,000 rows)  
✅ **Redis cache** (25 MB)  
✅ **Custom subdomain** (`yourapp.herokuapp.com`)  
✅ **Automatic deployments**  
✅ **Free SSL certificate**  

---

## Free Tier Limits:

- **550-1000 free dyno hours/month** (enough for always-on)
- **10,000 PostgreSQL rows** (plenty for testing)
- **25 MB Redis cache**
- App sleeps after 30 min of inactivity (wakes up in 5 seconds)

**Upgrade later if needed** (starting at $7/month for always-on)

---

## Next Steps (Optional)

### Configure Email (Gmail)
1. Generate Gmail App Password: https://myaccount.google.com/apppasswords
2. Set in Heroku:
```bash
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-16-char-app-password"
heroku config:set DEFAULT_FROM_EMAIL="BOOKCYCLE <noreply@yourdomain.com>"
```

### Add Custom Domain (Later)
```bash
heroku domains:add www.yourdomain.com
```

### Configure Cloudinary (Media Storage)
1. Sign up at https://cloudinary.com (free)
2. Get credentials
3. Set config:
```bash
heroku config:set USE_S3=False
heroku config:set CLOUDINARY_CLOUD_NAME="your-cloud-name"
heroku config:set CLOUDINARY_API_KEY="your-api-key"
heroku config:set CLOUDINARY_API_SECRET="your-api-secret"
```

---

## Continuous Deployment

Every time you make changes:

```bash
git add .
git commit -m "Description of changes"
git push heroku main
```

Heroku auto-deploys! 🎉

---

**Need help?** Check logs with `heroku logs --tail`

**Congratulations! Your marketplace is LIVE!** 🎊
