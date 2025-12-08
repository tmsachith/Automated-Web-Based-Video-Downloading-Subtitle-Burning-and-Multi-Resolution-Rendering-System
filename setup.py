"""
Setup and Validation Script
Run this to verify your installation and setup
"""
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ❌ ERROR: Python 3.8+ required")
        return False
    else:
        print("  ✓ Python version OK")
        return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg installation...")
    
    # Check ffmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f"  ✓ FFmpeg found: {ffmpeg_path}")
        
        # Get version
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stdout.split('\n')[0]
            print(f"  {version_line}")
        except:
            print("  ⚠ Could not get FFmpeg version")
    else:
        print("  ❌ FFmpeg NOT found in PATH")
        print("\n  Please install FFmpeg:")
        print("    Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("    Linux:   sudo apt install ffmpeg")
        print("    macOS:   brew install ffmpeg")
        return False
    
    # Check ffprobe
    ffprobe_path = shutil.which('ffprobe')
    if ffprobe_path:
        print(f"  ✓ FFprobe found: {ffprobe_path}")
    else:
        print("  ❌ FFprobe NOT found in PATH")
        return False
    
    return True

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\nChecking Python packages...")
    
    required_packages = {
        'flask': 'Flask',
        'requests': 'requests',
        'tqdm': 'tqdm'
    }
    
    all_installed = True
    
    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {display_name} installed")
        except ImportError:
            print(f"  ❌ {display_name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\n  Install missing packages with:")
        print("    pip install -r requirements.txt")
        return False
    
    return True

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directory structure...")
    
    required_dirs = [
        'downloads',
        'processing',
        'outputs',
        'logs',
        'temp',
        'templates'
    ]
    
    base_dir = Path(__file__).parent
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ⚠ {dir_name}/ created")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return True

def check_config():
    """Validate configuration"""
    print("\nValidating configuration...")
    
    try:
        from config import validate_config
        validate_config()
        print("  ✓ Configuration valid")
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def check_files():
    """Check if all required files exist"""
    print("\nChecking required files...")
    
    required_files = [
        'config.py',
        'logger.py',
        'downloader.py',
        'subtitle_processor.py',
        'video_encoder.py',
        'main.py',
        'web_app.py',
        'requirements.txt',
        'templates/index.html'
    ]
    
    base_dir = Path(__file__).parent
    all_exist = True
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ❌ {file_name} NOT found")
            all_exist = False
    
    return all_exist

def test_system():
    """Run a quick system test"""
    print("\nRunning system test...")
    
    try:
        # Import main components
        from config import RESOLUTIONS, DIRS
        from downloader import Downloader
        from subtitle_processor import SubtitleProcessor
        from video_encoder import VideoEncoder
        
        # Test configuration
        print(f"  ✓ Resolutions configured: {list(RESOLUTIONS.keys())}")
        print(f"  ✓ Output directory: {DIRS['outputs']}")
        
        # Test components
        downloader = Downloader()
        print("  ✓ Downloader initialized")
        
        processor = SubtitleProcessor()
        print("  ✓ Subtitle processor initialized")
        
        encoder = VideoEncoder()
        print("  ✓ Video encoder initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ System test failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print_header("SETUP COMPLETE!")
    
    print("🎉 Your system is ready to use!\n")
    
    print("Quick Start:\n")
    
    print("1. Web Interface (Recommended):")
    print("   python web_app.py")
    print("   Then open: http://localhost:5000\n")
    
    print("2. Command Line:")
    print("   python main.py --video <URL> --subtitle <URL>\n")
    
    print("3. Get Help:")
    print("   python main.py --help\n")
    
    print("Examples:\n")
    
    print("  # Process with all resolutions")
    print("  python main.py --video https://example.com/video.mp4 --subtitle https://example.com/sub.srt\n")
    
    print("  # Specific resolutions only")
    print("  python main.py --video URL --subtitle URL --resolutions 720p 1080p\n")
    
    print("  # Hard-burned subtitles")
    print("  python main.py --video URL --subtitle URL --hard-subtitle\n")
    
    print("📚 Documentation:")
    print("   - README.md for detailed usage")
    print("   - DEPLOYMENT.md for cloud deployment\n")
    
    print("=" * 80)

def main():
    """Main setup validation"""
    print_header("VIDEO PROCESSING SYSTEM - SETUP VALIDATION")
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("FFmpeg", check_ffmpeg()))
    checks.append(("Python Packages", check_python_packages()))
    checks.append(("Directories", check_directories()))
    checks.append(("Required Files", check_files()))
    checks.append(("Configuration", check_config()))
    checks.append(("System Test", test_system()))
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print_usage_instructions()
        return 0
    else:
        print("\n⚠ Some checks failed. Please address the issues above.\n")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    exit(main())
