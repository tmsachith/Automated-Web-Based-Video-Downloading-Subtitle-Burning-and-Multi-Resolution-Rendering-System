# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (5 minutes)

1. **Install Python 3.8+**
   - Already have it? Check with: `python --version`
   - Download: https://www.python.org/downloads/

2. **Install FFmpeg** (REQUIRED!)
   
   **Windows:**
   ```powershell
   # Option 1: Using winget (Windows 10+)
   winget install Gyan.FFmpeg
   
   # Option 2: Manual installation
   # Download from: https://www.gyan.dev/ffmpeg/builds/
   # Extract and add to PATH
   ```
   
   **Verify installation:**
   ```powershell
   ffmpeg -version
   ```

3. **Install Python packages:**
   ```powershell
   pip install -r requirements.txt
   ```

### Step 2: Verify Setup (1 minute)

```powershell
python setup.py
```

You should see all checks pass with ✓ marks.

### Step 3: Start Processing! (30 seconds)

**Option A: Web Interface** (Easiest)
```powershell
python web_app.py
```
Then open: http://localhost:5000

**Option B: Command Line**
```powershell
python main.py --video "VIDEO_URL" --subtitle "SUBTITLE_URL"
```

---

## 📝 Example Usage

### Test with a Small Video

```powershell
# Download a test video and subtitle first, then:
python main.py --video "path/to/video.mp4" --subtitle "path/to/subtitle.srt" --resolutions 720p
```

### Web Interface Workflow

1. Start server: `python web_app.py`
2. Open browser: http://localhost:5000
3. Enter video URL and subtitle URL
4. Select resolutions (360p, 480p, 720p, 1080p)
5. Choose subtitle mode (soft/hard)
6. Click "Start Processing"
7. Monitor progress in real-time
8. Download processed videos when ready

### Command Line Options

```powershell
# Process with all resolutions
python main.py --video URL --subtitle URL

# Specific resolutions only
python main.py --video URL --subtitle URL --resolutions 720p 1080p

# Hard-burned subtitles (permanently in video)
python main.py --video URL --subtitle URL --hard-subtitle

# Enable parallel encoding (faster on multi-core CPUs)
python main.py --video URL --subtitle URL --parallel

# Get help
python main.py --help
```

---

## 📂 Finding Your Output Files

After processing, find your videos in:
```
outputs/
├── 360p/
│   └── video_360p_subtitled.mp4
├── 480p/
│   └── video_480p_subtitled.mp4
├── 720p/
│   └── video_720p_subtitled.mp4
└── 1080p/
    └── video_1080p_subtitled.mp4
```

---

## ⚠️ Troubleshooting

### FFmpeg not found
```
❌ FFmpeg NOT found in PATH
```
**Fix:** Install FFmpeg and restart your terminal

### Module not found
```
ModuleNotFoundError: No module named 'flask'
```
**Fix:** `pip install -r requirements.txt`

### Download fails
```
Error: Failed to download
```
**Fix:** 
- Ensure URLs are direct download links (not web pages)
- Check internet connection
- Verify URLs are accessible

### Processing very slow
- Use fewer resolutions
- Disable parallel encoding
- Try hard subtitle instead of soft (or vice versa)
- Use smaller input video for testing

---

## 🎯 Next Steps

1. ✅ **Local Testing**: Test with small videos first
2. ✅ **Optimize Settings**: Edit `config.py` for your needs
3. ✅ **Cloud Deployment**: See `DEPLOYMENT.md` for cloud hosting
4. ✅ **Batch Processing**: Process multiple videos sequentially

---

## 📚 Documentation

- **README.md** - Complete documentation
- **DEPLOYMENT.md** - Cloud deployment guide
- **config.py** - All settings and configurations

---

## ⏱️ Processing Time Estimates

| Video Length | 720p Encoding | All Resolutions |
|--------------|---------------|-----------------|
| 5 minutes    | ~2-3 min      | ~8-12 min      |
| 30 minutes   | ~10-15 min    | ~40-60 min     |
| 2 hours      | ~40-60 min    | ~2.5-4 hours   |

*Times vary based on CPU speed and encoding settings*

---

## 💡 Tips for Success

1. **Start small** - Test with short videos (< 5 min) first
2. **One resolution** - Try single resolution before all 4
3. **Soft subtitles** - Faster than hard-burning
4. **Monitor logs** - Check `logs/processing.log` if issues occur
5. **Free space** - Ensure adequate disk space (3x video size)

---

**Need Help?** Run `python setup.py` to diagnose issues!
