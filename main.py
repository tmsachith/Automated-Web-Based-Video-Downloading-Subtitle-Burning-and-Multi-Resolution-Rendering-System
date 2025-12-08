"""
Main Processing Pipeline
Orchestrates the complete video processing workflow
"""
import uuid
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config import DIRS, PROCESSING_CONFIG, validate_config
from downloader import Downloader
from subtitle_processor import SubtitleProcessor
from video_encoder import VideoEncoder
from logger import logger, ProcessingError


class VideoProcessingPipeline:
    """Main orchestrator for the video processing system"""
    
    def __init__(self):
        """Initialize the processing pipeline"""
        # Validate configuration
        try:
            validate_config()
            logger.info("Configuration validated successfully")
        except Exception as e:
            logger.critical(f"Configuration validation failed: {e}")
            raise
        
        # Initialize components
        self.downloader = Downloader()
        self.subtitle_processor = SubtitleProcessor()
        self.video_encoder = VideoEncoder()
        
        logger.info("Video Processing Pipeline initialized")
    
    def generate_job_id(self) -> str:
        """Generate unique job identifier"""
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def cleanup_temp_files(self, files: List[Path]):
        """
        Clean up temporary processing files
        
        Args:
            files: List of file paths to remove
        """
        if not PROCESSING_CONFIG['cleanup_temp_files']:
            logger.info("Temp file cleanup disabled in config")
            return
        
        logger.info("Cleaning up temporary files...")
        for file_path in files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")
    
    def process_video(
        self,
        video_url: str,
        subtitle_url: str,
        resolutions: Optional[List[str]] = None,
        use_soft_subtitle: Optional[bool] = None
    ) -> Dict:
        """
        Complete video processing workflow
        
        Args:
            video_url: URL to video file
            subtitle_url: URL to subtitle file
            resolutions: List of target resolutions (default: all)
            use_soft_subtitle: Override subtitle embedding mode
            
        Returns:
            Dictionary with processing results
        """
        job_id = self.generate_job_id()
        start_time = time.time()
        temp_files = []
        
        logger.log_processing_start(video_url, subtitle_url)
        logger.info(f"Job ID: {job_id}")
        
        try:
            # Step 1: Download video and subtitle
            logger.info("\n" + "="*80)
            logger.info("STEP 1: Downloading video and subtitle files")
            logger.info("="*80)
            
            video_path, subtitle_path = self.downloader.download_video_and_subtitle(
                video_url,
                subtitle_url
            )
            temp_files.extend([video_path, subtitle_path])
            
            logger.info(f"✓ Video downloaded: {video_path}")
            logger.info(f"✓ Subtitle downloaded: {subtitle_path}")
            
            # Step 2: Process subtitles
            logger.info("\n" + "="*80)
            logger.info("STEP 2: Processing and embedding subtitles")
            logger.info("="*80)
            
            processed_video = self.subtitle_processor.process_subtitle(
                video_path,
                subtitle_path,
                use_soft_subtitle
            )
            temp_files.append(processed_video)
            
            logger.info(f"✓ Subtitles embedded: {processed_video}")
            
            # Step 3: Multi-resolution encoding
            logger.info("\n" + "="*80)
            logger.info("STEP 3: Multi-resolution video encoding")
            logger.info("="*80)
            
            output_files = self.video_encoder.encode_all_resolutions(
                processed_video,
                resolutions
            )
            
            # Step 4: Generate thumbnails (optional)
            logger.info("\n" + "="*80)
            logger.info("STEP 4: Generating preview thumbnails")
            logger.info("="*80)
            
            thumbnails = self.video_encoder.create_preview_thumbnails(processed_video)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare results
            results = {
                'job_id': job_id,
                'status': 'success',
                'processing_time': processing_time,
                'video_url': video_url,
                'subtitle_url': subtitle_url,
                'original_video': str(video_path),
                'subtitle_file': str(subtitle_path),
                'processed_video': str(processed_video),
                'output_files': {res: str(path) for res, path in output_files.items()},
                'thumbnails': [str(t) for t in thumbnails],
                'total_output_files': len(output_files),
                'processing_time_formatted': f"{int(processing_time // 60)}m {int(processing_time % 60)}s"
            }
            
            # Log completion
            logger.log_processing_complete(list(output_files.values()))
            logger.info(f"Total processing time: {results['processing_time_formatted']}")
            
            # Create job report
            report_path = logger.create_job_report(job_id, 'success', results)
            results['report_file'] = str(report_path)
            
            # Cleanup temporary files
            if PROCESSING_CONFIG['cleanup_temp_files']:
                if not PROCESSING_CONFIG['keep_original_files']:
                    self.cleanup_temp_files(temp_files)
                else:
                    # Keep downloaded files, remove only processing intermediates
                    self.cleanup_temp_files([processed_video])
            
            return results
            
        except Exception as e:
            # Log error
            logger.log_processing_error(e, "processing")
            
            # Create error report
            error_results = {
                'job_id': job_id,
                'status': 'failed',
                'error': str(e),
                'error_type': type(e).__name__,
                'video_url': video_url,
                'subtitle_url': subtitle_url,
                'processing_time': time.time() - start_time
            }
            
            logger.create_job_report(job_id, 'failed', error_results)
            
            # Re-raise exception
            raise ProcessingError(f"Video processing failed: {e}") from e


def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Video Processing System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --video https://example.com/video.mp4 --subtitle https://example.com/sub.srt
  python main.py --video URL --subtitle URL --resolutions 720p 1080p
  python main.py --video URL --subtitle URL --hard-subtitle
        """
    )
    
    parser.add_argument(
        '--video',
        required=True,
        help='URL to video file'
    )
    
    parser.add_argument(
        '--subtitle',
        required=True,
        help='URL to subtitle file'
    )
    
    parser.add_argument(
        '--resolutions',
        nargs='+',
        choices=['360p', '480p', '720p', '1080p'],
        help='Target resolutions (default: all)'
    )
    
    parser.add_argument(
        '--hard-subtitle',
        action='store_true',
        help='Burn subtitle into video (default: soft embed)'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel encoding'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*80)
    print("AUTOMATED VIDEO PROCESSING SYSTEM")
    print("="*80 + "\n")
    
    # Initialize pipeline
    pipeline = VideoProcessingPipeline()
    
    # Process video
    try:
        results = pipeline.process_video(
            video_url=args.video,
            subtitle_url=args.subtitle,
            resolutions=args.resolutions,
            use_soft_subtitle=not args.hard_subtitle
        )
        
        # Print results
        print("\n" + "="*80)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\nJob ID: {results['job_id']}")
        print(f"Processing Time: {results['processing_time_formatted']}")
        print(f"\nOutput Files ({results['total_output_files']}):")
        for resolution, filepath in results['output_files'].items():
            print(f"  [{resolution}] {filepath}")
        
        if results['thumbnails']:
            print(f"\nThumbnails ({len(results['thumbnails'])}):")
            for thumb in results['thumbnails']:
                print(f"  - {thumb}")
        
        print(f"\nReport: {results['report_file']}")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print("\n" + "="*80)
        print("PROCESSING FAILED!")
        print("="*80)
        print(f"\nError: {e}")
        print("\nCheck the log file for more details:")
        print(f"  {DIRS['logs'] / 'processing.log'}")
        print("\n" + "="*80 + "\n")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
