"""
Flask Web Application for Video Processing System
"""
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import threading
from datetime import datetime
import json

from config import WEB_CONFIG, DIRS
from main import VideoProcessingPipeline
from logger import logger

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = WEB_CONFIG['max_upload_size']

# Store active jobs
active_jobs = {}
completed_jobs = {}


class JobProcessor(threading.Thread):
    """Background thread for processing video jobs"""
    
    def __init__(self, job_id, video_url, subtitle_url, resolutions, use_soft_subtitle):
        super().__init__()
        self.job_id = job_id
        self.video_url = video_url
        self.subtitle_url = subtitle_url
        self.resolutions = resolutions
        self.use_soft_subtitle = use_soft_subtitle
        self.pipeline = VideoProcessingPipeline()
    
    def run(self):
        """Execute the processing job"""
        try:
            active_jobs[self.job_id]['status'] = 'processing'
            active_jobs[self.job_id]['stage'] = 'Downloading files'
            
            results = self.pipeline.process_video(
                self.video_url,
                self.subtitle_url,
                self.resolutions,
                self.use_soft_subtitle
            )
            
            # Move to completed jobs
            completed_jobs[self.job_id] = {
                'status': 'completed',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.job_id in active_jobs:
                del active_jobs[self.job_id]
                
        except Exception as e:
            logger.error(f"Job {self.job_id} failed: {e}")
            completed_jobs[self.job_id] = {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.job_id in active_jobs:
                del active_jobs[self.job_id]


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/submit', methods=['POST'])
def submit_job():
    """Submit a new processing job"""
    try:
        data = request.json
        
        video_url = data.get('video_url')
        subtitle_url = data.get('subtitle_url')
        resolutions = data.get('resolutions', ['360p', '480p', '720p', '1080p'])
        use_soft_subtitle = data.get('soft_subtitle', True)
        
        # Validate inputs
        if not video_url or not subtitle_url:
            return jsonify({
                'success': False,
                'error': 'Both video and subtitle URLs are required'
            }), 400
        
        # Generate job ID
        from main import VideoProcessingPipeline
        temp_pipeline = VideoProcessingPipeline()
        job_id = temp_pipeline.generate_job_id()
        
        # Create job entry
        active_jobs[job_id] = {
            'status': 'queued',
            'video_url': video_url,
            'subtitle_url': subtitle_url,
            'resolutions': resolutions,
            'soft_subtitle': use_soft_subtitle,
            'timestamp': datetime.now().isoformat(),
            'stage': 'Queued'
        }
        
        # Start processing thread
        processor = JobProcessor(job_id, video_url, subtitle_url, resolutions, use_soft_subtitle)
        processor.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Job submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to submit job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Get status of a specific job"""
    # Check active jobs
    if job_id in active_jobs:
        return jsonify({
            'job_id': job_id,
            'status': 'active',
            'details': active_jobs[job_id]
        })
    
    # Check completed jobs
    if job_id in completed_jobs:
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'details': completed_jobs[job_id]
        })
    
    return jsonify({
        'job_id': job_id,
        'status': 'not_found',
        'error': 'Job not found'
    }), 404


@app.route('/api/jobs')
def list_jobs():
    """List all jobs"""
    return jsonify({
        'active': active_jobs,
        'completed': completed_jobs
    })


@app.route('/api/download/<job_id>/<resolution>')
def download_file(job_id, resolution):
    """Download processed video file"""
    if job_id not in completed_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = completed_jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    output_files = job['results'].get('output_files', {})
    
    if resolution not in output_files:
        return jsonify({'error': 'Resolution not found'}), 404
    
    file_path = Path(output_files[resolution])
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_path.name
    )


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_jobs': len(active_jobs),
        'completed_jobs': len(completed_jobs)
    })


def run_web_app():
    """Start the Flask web application"""
    print("\n" + "="*80)
    print("AUTOMATED VIDEO PROCESSING SYSTEM - WEB INTERFACE")
    print("="*80)
    print(f"\nStarting web server on http://{WEB_CONFIG['host']}:{WEB_CONFIG['port']}")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*80 + "\n")
    
    app.run(
        host=WEB_CONFIG['host'],
        port=WEB_CONFIG['port'],
        debug=WEB_CONFIG['debug']
    )


if __name__ == '__main__':
    run_web_app()
