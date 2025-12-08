"""
Logging and Error Handling System
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG, DIRS

class ProcessingLogger:
    """Centralized logging system for video processing"""
    
    def __init__(self, name: str = 'VideoProcessor'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            LOG_CONFIG['log_file'],
            maxBytes=LOG_CONFIG['max_log_size'],
            backupCount=LOG_CONFIG['backup_count']
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_processing_start(self, video_url: str, subtitle_url: str):
        """Log the start of processing"""
        self.info("=" * 80)
        self.info(f"PROCESSING STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Video URL: {video_url}")
        self.info(f"Subtitle URL: {subtitle_url}")
        self.info("=" * 80)
    
    def log_processing_complete(self, output_files: list):
        """Log successful completion"""
        self.info("=" * 80)
        self.info(f"PROCESSING COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Generated {len(output_files)} output files:")
        for file in output_files:
            self.info(f"  - {file}")
        self.info("=" * 80)
    
    def log_processing_error(self, error: Exception, stage: str):
        """Log processing error"""
        self.error("=" * 80)
        self.error(f"PROCESSING FAILED at stage: {stage}")
        self.error(f"Error: {str(error)}")
        self.error(f"Error Type: {type(error).__name__}")
        self.error("=" * 80)
    
    def create_job_report(self, job_id: str, status: str, details: dict) -> Path:
        """
        Create a detailed job report
        
        Args:
            job_id: Unique job identifier
            status: Job status (success/failed)
            details: Dictionary with job details
            
        Returns:
            Path to the report file
        """
        report_dir = DIRS['logs'] / 'reports'
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"JOB REPORT\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Job ID: {job_id}\n")
            f.write(f"Status: {status}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 80}\n\n")
            
            for key, value in details.items():
                f.write(f"{key}: {value}\n")
        
        self.info(f"Job report created: {report_file}")
        return report_file


class ProcessingError(Exception):
    """Base exception for processing errors"""
    pass

class DownloadError(ProcessingError):
    """Exception raised for download failures"""
    pass

class SubtitleError(ProcessingError):
    """Exception raised for subtitle processing failures"""
    pass

class EncodingError(ProcessingError):
    """Exception raised for video encoding failures"""
    pass

class ValidationError(ProcessingError):
    """Exception raised for validation failures"""
    pass


# Global logger instance
logger = ProcessingLogger()


if __name__ == '__main__':
    # Test logging
    logger.info("Logger initialized successfully")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test job report
    test_details = {
        'video_file': 'test_video.mp4',
        'subtitle_file': 'test_subtitle.srt',
        'resolutions': '360p, 480p, 720p, 1080p',
        'duration': '2 minutes 30 seconds'
    }
    logger.create_job_report('TEST123', 'success', test_details)
    print(f"\nLog file location: {LOG_CONFIG['log_file']}")
