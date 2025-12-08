# Cloud Deployment Guide

## Overview
This guide covers deploying your video processing system to free cloud platforms.

## Platform Comparison

| Platform | Free Tier | Best For | Limitations |
|----------|-----------|----------|-------------|
| Railway | 500 hrs/month | Production apps | $5 credit/month |
| Render | 750 hrs/month | Web services | Spins down after inactivity |
| Fly.io | 3 VMs | Docker apps | 256MB RAM default |
| Google Colab | Unlimited* | Testing only | Sessions timeout |
| Kaggle | 30 hrs/week GPU | Batch processing | Manual execution |

## 1. Railway Deployment (Recommended)

### Prerequisites
- GitHub account
- Railway account (free)
- Git installed locally

### Steps

1. **Prepare your repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create `Procfile`:**
   ```
   web: python web_app.py
   ```

3. **Create `runtime.txt`:**
   ```
   python-3.10.0
   ```

4. **Create `railway.json`:**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "python web_app.py",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

5. **Install Railway CLI:**
   ```bash
   npm install -g railway
   ```

6. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

7. **Add FFmpeg buildpack:**
   - Go to Railway dashboard
   - Settings → Environment
   - Add buildpack: `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`

8. **Set environment variables:**
   ```bash
   railway variables set FLASK_ENV=production
   railway variables set WEB_HOST=0.0.0.0
   railway variables set WEB_PORT=5000
   ```

## 2. Render Deployment

### Steps

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: video-processor
       env: python
       buildCommand: "./build.sh"
       startCommand: "python web_app.py"
       envVars:
         - key: PYTHON_VERSION
           value: 3.10.0
   ```

2. **Create `build.sh`:**
   ```bash
   #!/usr/bin/env bash
   # Install FFmpeg
   apt-get update
   apt-get install -y ffmpeg
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Make executable:**
   ```bash
   chmod +x build.sh
   ```

4. **Deploy:**
   - Connect your GitHub repo to Render
   - Select "Web Service"
   - Choose your repository
   - Render will auto-deploy

## 3. Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Install FFmpeg and system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p downloads processing outputs logs temp

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "web_app.py"]
```

### Create `.dockerignore`

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
downloads/*
processing/*
outputs/*
logs/*
temp/*
.git
.gitignore
README.md
```

### Build and Run

```bash
# Build image
docker build -t video-processor .

# Run container
docker run -p 5000:5000 -v $(pwd)/outputs:/app/outputs video-processor

# Run with persistent storage
docker run -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/logs:/app/logs \
  video-processor
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  video-processor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
      - ./processing:/app/processing
      - ./outputs:/app/outputs
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - WEB_HOST=0.0.0.0
      - WEB_PORT=5000
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 4. Google Colab (Testing Only)

### Notebook Setup

```python
# Install dependencies
!pip install flask requests tqdm pyngrok

# Install FFmpeg
!apt-get update
!apt-get install -y ffmpeg

# Clone or upload your code
!git clone https://github.com/yourusername/video-processor.git
%cd video-processor

# Start with ngrok tunnel
from pyngrok import ngrok
import threading

# Start Flask in background
def run_app():
    from web_app import app
    app.run(host='0.0.0.0', port=5000)

thread = threading.Thread(target=run_app)
thread.start()

# Create public URL
public_url = ngrok.connect(5000)
print(f"Public URL: {public_url}")
```

## 5. Fly.io Deployment

### Prerequisites
- Fly.io account
- Flyctl CLI installed

### Steps

1. **Install Flyctl:**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Linux/Mac
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   flyctl auth login
   ```

3. **Initialize app:**
   ```bash
   flyctl launch
   ```

4. **Create `fly.toml`:**
   ```toml
   app = "your-app-name"
   
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     PORT = "5000"
   
   [[services]]
     internal_port = 5000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

5. **Deploy:**
   ```bash
   flyctl deploy
   ```

## 6. Environment Configuration

### Update `config.py` for Production

Add environment variable support:

```python
import os

# Web configuration with environment variables
WEB_CONFIG = {
    'host': os.getenv('WEB_HOST', '0.0.0.0'),
    'port': int(os.getenv('WEB_PORT', 5000)),
    'debug': os.getenv('FLASK_ENV') != 'production',
    'max_upload_size': 100 * 1024 * 1024,
    'allowed_hosts': ['localhost', '127.0.0.1']
}
```

## 7. Performance Optimization for Cloud

### Reduce Memory Usage

In `config.py`:
```python
PROCESSING_CONFIG = {
    'cleanup_temp_files': True,  # Clean up immediately
    'keep_original_files': False,  # Don't keep originals
    'batch_processing': False,
    'parallel_encoding': False  # Sequential to save memory
}
```

### Limit Resolutions

For low-memory environments:
```python
# Only generate essential resolutions
RESOLUTIONS = {
    '480p': {...},
    '720p': {...}
}
```

## 8. Monitoring and Logs

### Add Health Check Endpoint

Already included in `web_app.py`:
```
GET /health
```

### View Logs

**Railway:**
```bash
railway logs
```

**Render:**
- View in dashboard under "Logs"

**Docker:**
```bash
docker logs -f container_name
```

**Fly.io:**
```bash
flyctl logs
```

## 9. Storage Considerations

### Temporary File Management

Cloud platforms have limited storage. Ensure cleanup:

```python
# In config.py
PROCESSING_CONFIG = {
    'cleanup_temp_files': True,
    'keep_original_files': False
}
```

### External Storage (Optional)

For production, consider:
- AWS S3
- Google Cloud Storage
- Cloudinary
- Backblaze B2

## 10. Cost Management

### Free Tier Limits

- **Railway**: Monitor usage dashboard
- **Render**: 750 hours = ~31 days (but sleeps when inactive)
- **Fly.io**: 3 VMs with 256MB RAM each

### Tips to Stay Free

1. **Auto-sleep**: Let services sleep when inactive
2. **Limit resolutions**: Don't encode all 4 resolutions
3. **Sequential processing**: Disable parallel encoding
4. **Clean up**: Delete temp files immediately
5. **Monitor usage**: Check dashboards regularly

## 11. Security Considerations

### Production Checklist

- [ ] Set `debug=False` in production
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Validate all inputs
- [ ] Use HTTPS (handled by platforms)

### Add Rate Limiting (Optional)

```bash
pip install Flask-Limiter
```

In `web_app.py`:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["10 per minute"]
)
```

## 12. Troubleshooting

### Common Issues

**FFmpeg not found in cloud:**
- Ensure buildpack is installed
- Check build logs
- Verify apt-get install in build script

**Out of memory:**
- Disable parallel encoding
- Process fewer resolutions
- Increase VM size (may cost money)

**Timeout errors:**
- Use background jobs
- Implement job queue (Celery + Redis)
- Split large videos

**Storage full:**
- Enable aggressive cleanup
- Use external storage
- Process smaller batches

## Next Steps

1. Choose your platform (Railway recommended)
2. Follow the deployment steps
3. Test with small videos first
4. Monitor resource usage
5. Scale as needed

---

**Need Help?**
- Check platform documentation
- Review build logs
- Test locally with Docker first
- Start with smallest free tier
