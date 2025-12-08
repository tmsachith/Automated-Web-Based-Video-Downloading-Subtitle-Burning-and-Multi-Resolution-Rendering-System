# Automated Web-Based Video Downloading, Subtitle Integration, and Multi-Resolution Rendering System

A fully automated video processing platform that downloads videos and subtitles from the web, integrates subtitles (soft or hard), and renders videos in multiple resolutions (360p, 480p, 720p, 1080p).

## 🎯 Features

- **Automated Download**: Downloads video and subtitle files from direct URLs
- **Subtitle Integration**: Supports both soft embedding and hard burning of subtitles
- **Multi-Resolution Encoding**: Automatically generates 360p, 480p, 720p, and 1080p versions
- **Web Interface**: User-friendly web UI for submitting and monitoring jobs
- **Command-Line Interface**: Full CLI support for automation and scripting
- **Progress Tracking**: Real-time processing status and job monitoring
- **Error Handling**: Comprehensive logging and error reporting
- **100% Open Source**: Built with Python, FFmpeg, and Flask

## 📋 Prerequisites

### Required Software

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/

2. **FFmpeg** (Essential!)
   - **Windows**: 
     - Download from: https://www.gyan.dev/ffmpeg/builds/
     - Extract and add to system PATH
     - Or use: `winget install Gyan.FFmpeg`
   - **Linux**: 
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **macOS**: 
     ```bash
     brew install ffmpeg
     ```

3. **Verify FFmpeg Installation**
   ```bash
   ffmpeg -version
   ffprobe -version
   ```

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
cd "d:\Projects\Automated Web-Based Video Downloading, Subtitle Integration, and Multi-Resolution Rendering System"
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Configuration

```bash
python config.py
```

You should see:
```
Configuration loaded successfully!
Base directory: [your path]
Directories created: ['downloads', 'processing', 'outputs', 'logs', 'temp']
✓ FFmpeg is installed and accessible
```

## 💻 Usage

### Option 1: Web Interface (Recommended)

1. **Start the web server:**
   ```bash
   python web_app.py
   ```

2. **Open your browser:**
   ```
   http://localhost:5000
   ```

3. **Submit a job:**
   - Enter video URL
   - Enter subtitle URL
   - Select target resolutions
   - Choose subtitle mode (soft/hard)
   - Click "Start Processing"

4. **Monitor progress and download results** from the web interface

### Option 2: Command-Line Interface

**Basic usage:**
```bash
python main.py --video "https://example.com/video.mp4" --subtitle "https://example.com/subtitle.srt"
```

**Advanced usage:**
```bash
# Specific resolutions only
python main.py --video URL --subtitle URL --resolutions 720p 1080p

# Hard-burned subtitles
python main.py --video URL --subtitle URL --hard-subtitle

# Parallel encoding (faster on multi-core systems)
python main.py --video URL --subtitle URL --parallel
```

**Get help:**
```bash
python main.py --help
```

## 📁 Project Structure

```
├── config.py              # Configuration settings
├── logger.py              # Logging system
├── downloader.py          # Download manager
├── subtitle_processor.py  # Subtitle integration
├── video_encoder.py       # Video encoding engine
├── main.py                # CLI entry point
├── web_app.py             # Web interface
├── templates/
│   └── index.html         # Web UI template
├── requirements.txt       # Python dependencies
├── downloads/             # Downloaded files
├── processing/            # Temporary processing files
├── outputs/               # Final output videos
│   ├── 360p/
│   ├── 480p/
│   ├── 720p/
│   └── 1080p/
└── logs/                  # Processing logs
    └── reports/           # Job reports
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Resolution settings**: Bitrates, quality presets
- **Subtitle mode**: Default soft/hard subtitle preference
- **FFmpeg parameters**: Encoding settings, CRF values
- **Download settings**: Timeouts, retry attempts
- **Processing options**: Cleanup, parallel encoding
- **Web server**: Host, port, debug mode

## 🧪 Testing the System

### Test with Sample URLs

For testing, you can use these public domain video resources:

```bash
# Example with a test video (replace with actual URLs)
python main.py \
  --video "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4" \
  --subtitle "https://example.com/sample.srt" \
  --resolutions 360p 480p
```

### Verify Output

1. Check `outputs/` directory for encoded videos
2. Review `logs/processing.log` for detailed logs
3. Check `logs/reports/` for job reports

## 📊 Output Quality Settings

| Resolution | Video Bitrate | Audio Bitrate | Target Use Case |
|------------|---------------|---------------|-----------------|
| 360p       | 500 kbps      | 96 kbps       | Mobile, Low bandwidth |
| 480p       | 1000 kbps     | 128 kbps      | Mobile, Standard quality |
| 720p       | 2500 kbps     | 192 kbps      | HD, Desktop viewing |
| 1080p      | 5000 kbps     | 192 kbps      | Full HD, High quality |

## 🛠️ Troubleshooting

### FFmpeg Not Found
```
Error: FFmpeg not found in system PATH
```
**Solution**: Install FFmpeg and add to PATH, then restart terminal

### Download Failures
```
Error: Failed to download after 3 attempts
```
**Solutions**:
- Verify URLs are direct download links (not web pages)
- Check internet connection
- Try with `--no-verify-ssl` if SSL issues occur

### Encoding Errors
```
Error: FFmpeg encoding failed
```
**Solutions**:
- Check FFmpeg installation: `ffmpeg -version`
- Verify input video is valid
- Check available disk space
- Review logs in `logs/processing.log`

### Out of Memory
**Solutions**:
- Disable parallel encoding in `config.py`
- Process fewer resolutions at once
- Close other applications
- Increase system RAM/swap

## ☁️ Cloud Deployment Options

### Recommended Free Platforms

1. **Railway** (Recommended)
   - 500 hours/month free
   - Easy deployment
   - Supports background jobs

2. **Render**
   - 750 hours/month free
   - Auto-deploy from Git
   - Good for web apps

3. **Fly.io**
   - Limited free tier
   - Good performance
   - Docker support

4. **Google Colab** (Testing only)
   - Free GPU access
   - Great for testing
   - Temporary sessions

### Deployment Steps (Railway)

1. **Install Railway CLI:**
   ```bash
   npm install -g railway
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Set environment variables:**
   ```bash
   railway variables set FLASK_ENV=production
   ```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "web_app.py"]
```

Build and run:
```bash
docker build -t video-processor .
docker run -p 5000:5000 video-processor
```

## 📝 API Endpoints

### Web API

- `POST /api/submit` - Submit new processing job
- `GET /api/status/<job_id>` - Get job status
- `GET /api/jobs` - List all jobs
- `GET /api/download/<job_id>/<resolution>` - Download processed video
- `GET /health` - Health check

## 🔒 Legal & Ethical Use

**IMPORTANT**: This system is designed for:
- ✅ Personal video processing
- ✅ Legally owned or licensed content
- ✅ Open-source and public domain media
- ✅ Educational purposes

**NOT for**:
- ❌ Copyrighted content without permission
- ❌ Piracy or illegal downloading
- ❌ Violating terms of service
- ❌ Commercial use without proper licenses

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional subtitle formats support
- More encoding presets
- Batch processing UI
- Progress webhooks
- Cloud storage integration

## 📄 License

This project uses open-source tools:
- Python (PSF License)
- FFmpeg (GPL/LGPL)
- Flask (BSD License)

For personal and educational use only.

## 🆘 Support

For issues and questions:
1. Check `logs/processing.log`
2. Review this README
3. Verify FFmpeg installation
4. Check system requirements

## 🎓 Learning Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **Python Flask**: https://flask.palletsprojects.com/
- **Video Encoding Guide**: https://trac.ffmpeg.org/wiki/Encode/H.264

---

**Built with ❤️ using Python and FFmpeg**
