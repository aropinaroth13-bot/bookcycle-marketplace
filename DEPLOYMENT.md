# BOOKCYCLE Deployment Guide

## Prerequisites

Before deploying, ensure you have:
- [ ] PostgreSQL database
- [ ] Redis server
- [ ] AWS S3 bucket OR Cloudinary account
- [ ] Domain name with SSL certificate
- [ ] SMTP email service
- [ ] Stripe account (for payments - optional for now)

---

## Local Setup for Production Testing

### 1. Install Production Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `psycopg2-binary` - PostgreSQL adapter
- `django-redis` - Redis caching
- `boto3` - AWS S3 storage
- `django-storages` - Cloud storage backends
- `whitenoise` - Static file serving
- `gunicorn` - WSGI server
- `python-decouple` - Environment variables

### 2. PostgreSQL Setup

**Install PostgreSQL:**
```bash
# Windows (using Chocolatey)
choco install postgresql

# Or download from: https://www.postgresql.org/download/
```

**Create Database:**
```bash
psql -U postgres
CREATE DATABASE bookcycle_db;
CREATE USER bookcycle_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bookcycle_db TO bookcycle_user;
\q
```

### 3. Redis Setup

**Install Redis:**
```bash
# Windows (using Chocolatey)
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**Start Redis:**
```bash
redis-server
```

### 4. Environment Configuration

Copy `.env.production` to `.env`:
```bash
cp .env.production .env
```

Edit `.env` with your actual credentials.

### 5. Run Migrations

```bash
python manage.py migrate --settings=bookcycle.settings_production
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --settings=bookcycle.settings_production
```

### 7. Create Superuser

```bash
python manage.py createsuperuser --settings=bookcycle.settings_production
```

### 8. Test Production Server

```bash
gunicorn bookcycle.wsgi:application --bind 0.0.0.0:8000
```

---

## Deployment Platforms

### Option 1: Heroku

**Pros:** Easy, free tier available, automatic SSL  
**Cons:** Dyno sleeping on free tier

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name

# Add Buildpack
heroku buildpacks:set heroku/python

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set Environment Variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
# ... set all variables from .env.production

# Deploy
git push heroku main

# Run Migrations
heroku run python manage.py migrate

# Create Superuser
heroku run python manage.py createsuperuser
```

**Procfile** (create at root):
```
web: gunicorn bookcycle.wsgi:application --log-file -
release: python manage.py migrate
```

---

### Option 2: DigitalOcean App Platform

**Pros:** Affordable, managed databases, good India region support  
**Cons:** Requires payment info

1. Push code to GitHub
2. Go to DigitalOcean App Platform
3. Connect GitHub repository
4. Add PostgreSQL database
5. Add Redis cluster
6. Configure environment variables
7. Deploy

---

### Option 3: AWS (EC2 + RDS + ElastiCache)

**Pros:** Full control, scalable, professional  
**Cons:** More complex, higher cost

**Setup Steps:**
1. Launch EC2 instance (Ubuntu 22.04)
2. Create RDS PostgreSQL database
3. Create ElastiCache Redis cluster
4. Create S3 bucket for media
5. Configure security groups
6. Install Nginx + Gunicorn
7. Set up SSL with Let's Encrypt
8. Configure systemd service

---

### Option 4: Railway.app

**Pros:** Very easy, modern, affordable  
**Cons:** Newer platform

1. Connect GitHub repository
2. Add PostgreSQL plugin
3. Add Redis plugin
4. Set environment variables
5. Deploy automatically

---

## Production Checklist

### Security
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CSP headers
- [ ] Change admin URL
- [ ] Set up firewall rules

### Performance
- [ ] Enable Redis caching
- [ ] Configure CDN for static files
- [ ] Enable gzip compression
- [ ] Set up database connection pooling
- [ ] Configure proper logging

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring
- [ ] Enable application logging
- [ ] Set up database backups
- [ ] Configure email alerts

### Media Storage
- [ ] Configure S3 OR Cloudinary
- [ ] Set CORS policies
- [ ] Enable CDN for media files
- [ ] Configure file upload limits

### Email
- [ ] Configure SMTP settings
- [ ] Test email delivery
- [ ] Set up SPF/DKIM records
- [ ] Configure email templates

### Database
- [ ] Run all migrations
- [ ] Create database backups
- [ ] Set up backup schedule
- [ ] Configure connection pooling
- [ ] Optimize database queries

---

## Environment Variables Guide

### Required Variables
- `SECRET_KEY` - Django secret (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- `DEBUG` - Set to `False`
- `ALLOWED_HOSTS` - Your domain(s)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

### Optional But Recommended
- Redis URL
- Email configuration
- S3 or Cloudinary credentials
- Stripe keys (when ready)

---

## Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
python manage.py collectstatic --noinput
```

### Database Connection Issues
- Check PostgreSQL is running
- Verify credentials in `.env`
- Check security group/firewall rules
- Test connection: `psql -h HOST -U USER -d DATABASE`

### Redis Connection Issues
- Check Redis is running: `redis-cli ping`
- Verify REDIS_URL in `.env`
- Check firewall allows port 6379

### Media Files Not Uploading
- Check S3 bucket permissions
- Verify AWS credentials
- Check CORS configuration
- Test with local storage first

---

## Post-Deployment Tasks

1. **Test all features:**
   - User registration
   - Book listing
   - Search functionality
   - Cart and checkout
   - Reviews and ratings
   - Messaging system

2. **Monitor performance:**
   - Check server response times
   - Monitor error logs
   - Track database queries
   - Review cache hit rates

3. **Set up backups:**
   - Database daily backups
   - Media files weekly backups
   - Configuration backups

4. **Configure monitoring:**
   - Set up Sentry for error tracking
   - Enable uptime monitoring
   - Configure email alerts

---

## Scaling Considerations

As your application grows:
- Use database read replicas
- Implement CDN for static/media files
- Add load balancer for multiple servers
- Consider container orchestration (Kubernetes)
- Separate celery workers for background tasks

---

## Support & Resources

- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Redis Docs: https://redis.io/documentation
- AWS S3 Guide: https://docs.aws.amazon.com/s3/
- Heroku Django: https://devcenter.heroku.com/articles/django-app-configuration
