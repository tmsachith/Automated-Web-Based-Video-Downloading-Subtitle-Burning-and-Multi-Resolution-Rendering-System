"""
Test Script - Verify System Components
Run this to test individual components before processing real videos
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "="*80)
    print("TEST 1: Module Imports")
    print("="*80)
    
    modules = [
        'config',
        'logger',
        'downloader',
        'subtitle_processor',
        'video_encoder',
        'main',
        'web_app'
    ]
    
    failed = []
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            failed.append(module_name)
    
    return len(failed) == 0

def test_configuration():
    """Test configuration loading"""
    print("\n" + "="*80)
    print("TEST 2: Configuration")
    print("="*80)
    
    try:
        from config import (
            RESOLUTIONS, DIRS, FFMPEG_CONFIG, 
            SUBTITLE_CONFIG, DOWNLOAD_CONFIG, validate_config
        )
        
        print(f"  ✓ Resolutions: {list(RESOLUTIONS.keys())}")
        print(f"  ✓ Directories: {list(DIRS.keys())}")
        print(f"  ✓ Video codec: {FFMPEG_CONFIG['video_codec']}")
        print(f"  ✓ Audio codec: {FFMPEG_CONFIG['audio_codec']}")
        print(f"  ✓ Subtitle mode: {'Soft' if SUBTITLE_CONFIG['soft_subtitle'] else 'Hard'}")
        
        # Validate
        validate_config()
        print("  ✓ Configuration validated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_logger():
    """Test logging system"""
    print("\n" + "="*80)
    print("TEST 3: Logging System")
    print("="*80)
    
    try:
        from logger import logger
        
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        
        print("  ✓ Logger initialized")
        print("  ✓ Test messages logged")
        
        # Create test report
        test_details = {
            'test': 'system_test',
            'status': 'running'
        }
        report = logger.create_job_report('TEST_001', 'testing', test_details)
        print(f"  ✓ Job report created: {report}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Logger error: {e}")
        return False

def test_downloader():
    """Test download manager"""
    print("\n" + "="*80)
    print("TEST 4: Download Manager")
    print("="*80)
    
    try:
        from downloader import Downloader
        
        downloader = Downloader()
        print("  ✓ Downloader initialized")
        
        # Test URL validation
        valid = downloader.validate_url("https://example.com/video.mp4")
        invalid = downloader.validate_url("not-a-url")
        
        if valid and not invalid:
            print("  ✓ URL validation working")
        else:
            print("  ❌ URL validation failed")
            return False
        
        # Test filename extraction
        url = "https://example.com/path/movie.mp4?param=value"
        filename = downloader.get_filename_from_url(url)
        print(f"  ✓ Filename extraction: {filename}")
        
        # Test file type validation
        video_valid = downloader.validate_file_type("test.mp4", "video")
        sub_valid = downloader.validate_file_type("test.srt", "subtitle")
        
        if video_valid and sub_valid:
            print("  ✓ File type validation working")
        else:
            print("  ❌ File type validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Downloader error: {e}")
        return False

def test_subtitle_processor():
    """Test subtitle processor"""
    print("\n" + "="*80)
    print("TEST 5: Subtitle Processor")
    print("="*80)
    
    try:
        from subtitle_processor import SubtitleProcessor
        
        processor = SubtitleProcessor()
        print("  ✓ Subtitle processor initialized")
        print(f"  ✓ Mode: {'Soft' if processor.soft_subtitle else 'Hard'} subtitle")
        print(f"  ✓ Codec: {processor.subtitle_codec}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Subtitle processor error: {e}")
        return False

def test_video_encoder():
    """Test video encoder"""
    print("\n" + "="*80)
    print("TEST 6: Video Encoder")
    print("="*80)
    
    try:
        from video_encoder import VideoEncoder
        
        encoder = VideoEncoder()
        print("  ✓ Video encoder initialized")
        print(f"  ✓ Video codec: {encoder.video_codec}")
        print(f"  ✓ Audio codec: {encoder.audio_codec}")
        print(f"  ✓ Resolutions: {list(encoder.resolutions.keys())}")
        
        # Test dimension calculation
        width = encoder.calculate_output_width(1920, 1080, 720)
        print(f"  ✓ Dimension calculation: 1920x1080 → {width}x720")
        
        if width == 1280:
            print("  ✓ Aspect ratio calculation correct")
        else:
            print(f"  ⚠ Expected width 1280, got {width}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Video encoder error: {e}")
        return False

def test_pipeline():
    """Test main pipeline"""
    print("\n" + "="*80)
    print("TEST 7: Processing Pipeline")
    print("="*80)
    
    try:
        from main import VideoProcessingPipeline
        
        pipeline = VideoProcessingPipeline()
        print("  ✓ Pipeline initialized")
        
        # Test job ID generation
        job_id = pipeline.generate_job_id()
        print(f"  ✓ Job ID generated: {job_id}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline error: {e}")
        return False

def test_web_app():
    """Test web application"""
    print("\n" + "="*80)
    print("TEST 8: Web Application")
    print("="*80)
    
    try:
        from web_app import app
        
        print("  ✓ Flask app initialized")
        print(f"  ✓ App name: {app.name}")
        
        # Check routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/api/submit', '/api/status/<job_id>', '/health']
        
        for route in expected_routes:
            if route in routes:
                print(f"  ✓ Route exists: {route}")
            else:
                print(f"  ❌ Route missing: {route}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web app error: {e}")
        return False

def test_ffmpeg_commands():
    """Test FFmpeg is accessible"""
    print("\n" + "="*80)
    print("TEST 9: FFmpeg Commands")
    print("="*80)
    
    import subprocess
    
    commands = ['ffmpeg', 'ffprobe']
    
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"  ✓ {cmd}: {version_line[:60]}...")
            else:
                print(f"  ❌ {cmd} failed with code {result.returncode}")
                return False
                
        except FileNotFoundError:
            print(f"  ❌ {cmd} not found in PATH")
            return False
        except Exception as e:
            print(f"  ❌ {cmd} error: {e}")
            return False
    
    return True

def test_directory_structure():
    """Test directory structure"""
    print("\n" + "="*80)
    print("TEST 10: Directory Structure")
    print("="*80)
    
    try:
        from config import DIRS
        
        for name, path in DIRS.items():
            if path.exists():
                print(f"  ✓ {name:12} {path}")
            else:
                print(f"  ❌ {name:12} NOT FOUND: {path}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Directory error: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "="*80)
    print(" VIDEO PROCESSING SYSTEM - COMPONENT TESTS")
    print("="*80)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Logging System", test_logger),
        ("Download Manager", test_downloader),
        ("Subtitle Processor", test_subtitle_processor),
        ("Video Encoder", test_video_encoder),
        ("Processing Pipeline", test_pipeline),
        ("Web Application", test_web_app),
        ("FFmpeg Commands", test_ffmpeg_commands),
        ("Directory Structure", test_directory_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed")
    print("-"*80 + "\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour system is ready to use:")
        print("  • Web Interface: python web_app.py")
        print("  • Command Line:  python main.py --help")
        print("\n" + "="*80 + "\n")
        return 0
    else:
        print("⚠ SOME TESTS FAILED!")
        print("\nPlease address the failed tests above.")
        print("Run 'python setup.py' for diagnosis.\n")
        print("="*80 + "\n")
        return 1

if __name__ == '__main__':
    exit(run_all_tests())
