"""
Subtitle Integration Module
Handles soft embedding and hard burning of subtitles with proper Sinhala support
"""
import subprocess
import json
import os
import re
import time
from pathlib import Path
from typing import Optional, Dict

from config import SUBTITLE_CONFIG, DIRS, FFMPEG_CONFIG
from logger import logger, SubtitleError
from utils.subtitle_utils import (
    convert_srt_to_ass,
    find_font,
    detect_ffmpeg_shaping,
    escape_ffmpeg_path_for_filter,
    validate_sinhala_font_support
)


class SubtitleProcessor:
    """Processes and embeds subtitles into video files"""
    
    def __init__(self):
        self.soft_subtitle = SUBTITLE_CONFIG['soft_subtitle']
        self.subtitle_codec = SUBTITLE_CONFIG['subtitle_codec']
        self.burn_style = SUBTITLE_CONFIG['burn_style']
        
        # Detect FFmpeg capabilities on initialization
        self.shaping_support = detect_ffmpeg_shaping()
        if not self.shaping_support['ffmpeg_found']:
            logger.error("FFmpeg not found in system PATH!")
        elif not self.shaping_support['libass']:
            logger.warning("FFmpeg does not have libass support - subtitle rendering may fail")
        elif not self.shaping_support['harfbuzz']:
            logger.warning("FFmpeg libass lacks HarfBuzz - complex script shaping (Sinhala) may be incorrect")
        else:
            logger.info("✓ FFmpeg has libass + HarfBuzz support for proper Sinhala rendering")
    
    def find_sinhala_font(self) -> tuple[Path, str]:
        """
        Find available Sinhala font from project Fonts folder or system
        
        Returns:
            Tuple of (font_path, font_family_name)
        """
        # Get fonts directory
        project_fonts = DIRS.get('fonts', Path('Fonts'))
        if not isinstance(project_fonts, Path):
            project_fonts = Path('Fonts')
        
        # List of Sinhala fonts to try (in priority order)
        # Bindumathi is preferred for Sinhala, followed by Noto Sans Sinhala
        candidate_fonts = [
            'bindumathi.ttf',
            'Bindumathi.ttf',
            'NotoSansSinhala-Regular.ttf',
            'NotoSansSinhala.ttf',
            'NotoSansSinhala-Bold.ttf',
        ]
        
        font_path, font_family = find_font(candidate_fonts, project_fonts)
        
        # Validate the font
        if font_path and font_path.exists():
            if validate_sinhala_font_support(font_path):
                logger.info(f"✓ Found valid Sinhala font: {font_path} (family: {font_family})")
                return font_path, font_family
            else:
                logger.warning(f"Font found but may not support Sinhala properly: {font_path}")
        
        # Return what we found even if validation failed
        return font_path, font_family
    
    def get_video_info(self, video_path: Path) -> Dict:
        """
        Get video metadata using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            info = json.loads(result.stdout)
            
            # Extract relevant information
            video_stream = next(
                (s for s in info['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise SubtitleError("No video stream found")
            
            return {
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'duration': float(info['format'].get('duration', 0)),
                'bit_rate': int(info['format'].get('bit_rate', 0)),
                'codec': video_stream.get('codec_name', 'unknown'),
                'fps': eval(video_stream.get('r_frame_rate', '0/1'))
            }
            
        except subprocess.CalledProcessError as e:
            raise SubtitleError(f"Failed to get video info: {e.stderr}")
        except Exception as e:
            raise SubtitleError(f"Error reading video metadata: {e}")
    
    def validate_subtitle_file(self, subtitle_path: Path) -> bool:
        """
        Validate subtitle file format and ensure UTF-8 encoding
        
        Args:
            subtitle_path: Path to subtitle file
            
        Returns:
            True if valid
        """
        if not subtitle_path.exists():
            raise SubtitleError(f"Subtitle file not found: {subtitle_path}")
        
        # Check if file is readable and not empty
        if subtitle_path.stat().st_size == 0:
            raise SubtitleError(f"Subtitle file is empty: {subtitle_path}")
        
        # Ensure subtitle file is UTF-8 encoded
        try:
            content = subtitle_path.read_text(encoding='utf-8')
            # If we can read it as UTF-8, re-write to ensure BOM-free UTF-8
            subtitle_path.write_text(content, encoding='utf-8')
            logger.info(f"Subtitle file validated and ensured UTF-8: {subtitle_path}")
        except UnicodeDecodeError:
            # Try to read with different encodings and convert to UTF-8
            logger.warning("Subtitle file is not UTF-8, attempting to convert...")
            for encoding in ['utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content = subtitle_path.read_text(encoding=encoding)
                    subtitle_path.write_text(content, encoding='utf-8')
                    logger.info(f"Converted subtitle from {encoding} to UTF-8")
                    break
                except:
                    continue
            else:
                raise SubtitleError("Could not decode subtitle file with any known encoding")
        
        return True
    
    def embed_soft_subtitle(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Embed subtitle as a soft subtitle track (not burned in)
        
        Args:
            video_path: Path to input video
            subtitle_path: Path to subtitle file
            output_path: Optional output path
            
        Returns:
            Path to output video with embedded subtitles
        """
        logger.info("Embedding soft subtitles...")
        
        self.validate_subtitle_file(subtitle_path)
        
        if not output_path:
            output_path = DIRS['processing'] / f"{video_path.stem}_subtitled.mp4"
        
        try:
            # FFmpeg command for soft subtitle embedding with UTF-8 support
            # -sub_charenc utf-8 ensures proper Unicode/Sinhala character handling
            cmd = [
                'ffmpeg',
                '-sub_charenc', 'utf-8',  # Force UTF-8 encoding for subtitles
                '-i', str(video_path),
                '-i', str(subtitle_path),
                '-c:v', 'copy',  # Copy video stream (no re-encoding)
                '-c:a', 'copy',  # Copy audio stream
                '-c:s', self.subtitle_codec,  # Subtitle codec
                '-metadata:s:s:0', 'language=sin',  # Set subtitle language to Sinhala
                '-metadata:s:s:0', 'title=Sinhala',  # Set subtitle title
                '-disposition:s:0', 'default',  # Make subtitle default
                '-y',  # Overwrite output
                str(output_path)
            ]
            
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_path.exists():
                logger.info(f"Soft subtitles embedded successfully: {output_path}")
                return output_path
            else:
                raise SubtitleError("Output file was not created")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg stderr: {e.stderr}")
            raise SubtitleError(f"Failed to embed soft subtitles: {e.stderr}")
    
    def embed_hard_subtitle(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Optional[Path] = None,
        progress_callback=None,
        cancel_check=None
    ) -> Path:
        """
        Burn subtitle permanently into video frames (hard subtitle)
        WARNING: This is very slow (10-30 minutes) and CPU-intensive!
        
        Uses ASS format with proper font configuration for Sinhala rendering.
        
        Args:
            video_path: Path to input video
            subtitle_path: Path to subtitle file (SRT or ASS)
            output_path: Optional output path
            progress_callback: Function(current_seconds, total_seconds) for progress
            cancel_check: Optional function() -> bool to check for cancellation
            
        Returns:
            Path to output video with burned subtitles
        """
        logger.info("=" * 60)
        logger.info("HARD SUBTITLE BURNING - Sinhala-optimized pipeline")
        logger.info("=" * 60)
        
        # Check FFmpeg capabilities
        if not self.shaping_support['libass']:
            raise SubtitleError(
                "Hard subtitle rendering requires FFmpeg with libass support.\n"
                "Current FFmpeg build does not include libass.\n"
                "Options:\n"
                "1) Install FFmpeg with libass (recommended: use static build)\n"
                "2) Use soft subtitles instead (much faster, --soft-subtitle flag)"
            )
        
        if not self.shaping_support['harfbuzz']:
            logger.warning(
                "⚠ FFmpeg libass lacks HarfBuzz support!\n"
                "Sinhala character shaping may be INCORRECT (characters appear broken).\n"
                "For proper Sinhala rendering:\n"
                "1) Use FFmpeg static build with libass+HarfBuzz\n"
                "2) Or use soft subtitles with attached font (recommended)\n"
                "Proceeding anyway, but expect rendering issues..."
            )
        
        self.validate_subtitle_file(subtitle_path)
        
        if not output_path:
            output_path = DIRS['processing'] / f"{video_path.stem}_hardsubbed.mp4"
        
        # Import here to avoid circular dependency
        from config import PROCESSING_CONFIG
        low_memory = PROCESSING_CONFIG.get('low_memory_mode', False)
        
        # Get temp directory
        temp_dir = DIRS.get('temp', Path('temp'))
        if not isinstance(temp_dir, Path):
            temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            # STEP 1: Convert SRT to ASS if needed
            if subtitle_path.suffix.lower() == '.srt':
                logger.info("Converting SRT to ASS format for better rendering...")
                ass_temp = temp_dir / (subtitle_path.stem + ".ass")
                
                # Find Sinhala font
                font_path, font_family = self.find_sinhala_font()
                logger.info(f"Using font family: {font_family}")
                
                # Convert with detected font
                convert_srt_to_ass(
                    subtitle_path,
                    ass_temp,
                    fontname=font_family,
                    fontsize=36
                )
                subtitle_file_to_use = ass_temp
            else:
                logger.info("Using existing ASS file")
                subtitle_file_to_use = subtitle_path
            
            # STEP 2: Setup fonts directory
            project_fonts = DIRS.get('fonts', Path('Fonts'))
            if not isinstance(project_fonts, Path):
                project_fonts = Path('Fonts')
            
            # Create fonts.conf for fontconfig
            fonts_conf_content = f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>{project_fonts.absolute()}</dir>
  <cachedir>{temp_dir.absolute() / 'fontconfig-cache'}</cachedir>
</fontconfig>
"""
            fonts_conf_path = temp_dir / 'fonts.conf'
            fonts_conf_path.write_text(fonts_conf_content, encoding='utf-8')
            logger.info(f"Created fonts.conf: {fonts_conf_path}")
            
            # Set environment variable for fontconfig
            os.environ['FONTCONFIG_FILE'] = str(fonts_conf_path.absolute())
            logger.info(f"Set FONTCONFIG_FILE={os.environ['FONTCONFIG_FILE']}")
            
            # STEP 3: Prepare FFmpeg filter paths
            fonts_dir_abs = escape_ffmpeg_path_for_filter(str(project_fonts.absolute()))
            subtitle_file_abs = escape_ffmpeg_path_for_filter(str(subtitle_file_to_use.absolute()))
            
            logger.info(f"Fonts directory: {fonts_dir_abs}")
            logger.info(f"Subtitle file: {subtitle_file_abs}")
            
            # STEP 4: Build subtitle filter
            # Using subtitles filter with fontsdir and charenc for proper Sinhala rendering
            subtitle_filter = f"subtitles='{subtitle_file_abs}':fontsdir='{fonts_dir_abs}':charenc=UTF-8"
            
            # STEP 5: Add watermark if needed
            watermark_text = "This is MovieDownloadSL..."
            arial_path = project_fonts / 'arial.ttf'
            if arial_path.exists():
                arial_font = escape_ffmpeg_path_for_filter(str(arial_path.absolute()))
            else:
                arial_font = 'C:/Windows/Fonts/arial.ttf'
            
            watermark_filter = f"drawtext=text='{watermark_text}':fontfile={arial_font}:fontsize=24:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=30:enable='lt(t,10)'"
            
            # Combine filters
            combined_filter = f"{subtitle_filter},{watermark_filter}"
            logger.info(f"Video filter: {combined_filter}")
            
            # STEP 6: Memory-optimized settings
            if low_memory:
                logger.info("Using low-memory optimization for cloud environment")
                preset = 'veryfast'
                crf = 28
                threads = 2
            else:
                preset = FFMPEG_CONFIG['preset']
                crf = FFMPEG_CONFIG['crf']
                threads = 0
            
            # STEP 7: Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-vf', combined_filter,
                '-c:v', FFMPEG_CONFIG['video_codec'],
                '-crf', str(crf),
                '-preset', preset,
                '-threads', str(threads),
                '-c:a', 'copy',
                '-max_muxing_queue_size', '1024',
                str(output_path)
            ]
            
            logger.info("FFmpeg command:")
            logger.info(" ".join(cmd))
            logger.warning("⚠ HARD SUBTITLE BURNING IS VERY SLOW (10-30 min)!")
            logger.warning("💡 For production, use SOFT SUBTITLES (takes <1 minute)")
            logger.info("Processing every video frame with subtitle overlay...")
            
            # STEP 8: Get video duration for progress
            video_info = self.get_video_info(video_path)
            total_duration = video_info.get('duration', 0)
            
            # STEP 9: Run FFmpeg with progress monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Monitor progress
            for line in process.stdout:
                # Check for cancellation
                if cancel_check and cancel_check():
                    logger.warning("Cancelling hard subtitle burning...")
                    process.terminate()
                    time.sleep(0.5)
                    if process.poll() is None:
                        process.kill()
                    if output_path.exists():
                        output_path.unlink()
                    raise SubtitleError("Hard subtitle burning cancelled by user")
                
                if 'time=' in line:
                    # Parse FFmpeg progress
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if time_match and total_duration > 0:
                        hours, minutes, seconds = map(float, time_match.groups())
                        current_seconds = hours * 3600 + minutes * 60 + seconds
                        
                        if progress_callback:
                            progress_callback(current_seconds, total_duration)
                        
                        # Log progress every 10%
                        progress_pct = (current_seconds / total_duration) * 100
                        if int(progress_pct) % 10 == 0:
                            logger.info(f"Progress: {progress_pct:.1f}% ({current_seconds:.0f}/{total_duration:.0f}s)")
            
            process.wait()
            
            # STEP 10: Check result
            if process.returncode != 0:
                error_msg = f"FFmpeg process failed with code {process.returncode}"
                
                if process.returncode == -9:
                    error_msg += " (Process killed - likely out of memory. Try soft subtitles or upgrade server)"
                elif process.returncode == 137:
                    error_msg += " (Out of memory. Use soft subtitles instead)"
                elif process.returncode == 1:
                    error_msg += " (Encoding error - check video format and subtitle file)"
                
                logger.error(error_msg)
                raise SubtitleError(error_msg)
            
            if output_path.exists():
                file_size = output_path.stat().st_size / (1024 * 1024)
                logger.info("=" * 60)
                logger.info(f"✓ Hard subtitles burned successfully!")
                logger.info(f"Output: {output_path}")
                logger.info(f"Size: {file_size:.2f} MB")
                logger.info("=" * 60)
                return output_path
            else:
                raise SubtitleError("Output file was not created")
                
        except subprocess.CalledProcessError as e:
            raise SubtitleError(f"Failed to burn hard subtitles: {e}")
        except Exception as e:
            error_str = str(e)
            if 'killed' in error_str.lower() or 'code -9' in error_str:
                raise SubtitleError(
                    f"Process killed by system (out of memory).\n"
                    f"Recommendations:\n"
                    f"1) Use soft subtitles instead (--soft-subtitle)\n"
                    f"2) Upgrade server RAM\n"
                    f"3) Process video on more powerful machine\n"
                    f"Original error: {e}"
                )
            raise SubtitleError(f"Unexpected error during subtitle burning: {e}")
    
    def process_subtitle(
        self,
        video_path: Path,
        subtitle_path: Path,
        use_soft_subtitle: Optional[bool] = None,
        progress_callback=None,
        cancel_check=None
    ) -> Path:
        """
        Process subtitle based on configuration (soft or hard)
        
        Args:
            video_path: Path to video file
            subtitle_path: Path to subtitle file
            use_soft_subtitle: Override config setting
            progress_callback: Function(current, total) for progress updates
            cancel_check: Optional function() -> bool to check for cancellation
            
        Returns:
            Path to processed video
        """
        soft_sub = use_soft_subtitle if use_soft_subtitle is not None else self.soft_subtitle
        
        logger.info(f"Processing {'soft' if soft_sub else 'hard'} subtitles...")
        
        # Get video info
        video_info = self.get_video_info(video_path)
        logger.info(
            f"Video info: {video_info['width']}x{video_info['height']}, "
            f"{video_info['duration']:.2f}s, {video_info['codec']}"
        )
        
        if soft_sub:
            logger.info("Γ£ô Soft subtitles are FAST (~1 minute)")
            return self.embed_soft_subtitle(video_path, subtitle_path)
        else:
            logger.warning("ΓÜá∩╕Å Hard subtitles are VERY SLOW (10-30 minutes)!")
            logger.warning("≡ƒÆí Consider using soft subtitles for production")
            return self.embed_hard_subtitle(video_path, subtitle_path, progress_callback=progress_callback, cancel_check=cancel_check)


if __name__ == '__main__':
    # Test subtitle processor
    processor = SubtitleProcessor()
    print(f"Subtitle mode: {'Soft' if processor.soft_subtitle else 'Hard'}")
    print("Subtitle processor initialized successfully!")
