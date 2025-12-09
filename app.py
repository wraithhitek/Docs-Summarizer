#!/usr/bin/env python3
"""Web UI for Content Summarizer using Flask."""

from flask import Flask, render_template, request, jsonify, send_file, make_response
from pathlib import Path
from dotenv import load_dotenv
import os

from src.config import Config, ConfigurationError
from src.summarizer import (
    GeminiSummarizer,
    InvalidContentError,
    AuthenticationError,
    GeminiServiceError,
    ResponseParseError,
    RateLimitError,
    ModelNotAvailableError,
    InvalidRequestError,
    NetworkError,
    FileReadError
)
from src.database import SummaryDatabase
from src.export import SummaryExporter

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize summarizer and database
try:
    config = Config.from_env()
    summarizer = GeminiSummarizer(config)
    db = SummaryDatabase()
    exporter = SummaryExporter()
except Exception as e:
    print(f"Error initializing application: {e}")
    summarizer = None
    db = None
    exporter = None


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle summarization requests."""
    try:
        # Check if summarizer is initialized
        if summarizer is None or db is None:
            return jsonify({
                'success': False,
                'error': 'Summarizer not initialized. Please check your configuration.'
            }), 500

        # Get input method and style
        input_method = request.form.get('input_method', 'text')
        summary_style = request.form.get('style', 'standard')
        
        if input_method == 'text':
            # Get text from form
            content = request.form.get('content', '').strip()
            if not content:
                return jsonify({
                    'success': False,
                    'error': 'Please provide text content to summarize.'
                }), 400
        
        elif input_method == 'file':
            # Get uploaded file
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file uploaded.'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected.'
                }), 400
            
            # Read file content
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'File must be UTF-8 encoded text.'
                }), 400
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid input method.'
            }), 400
        
        # Perform summarization with selected style
        result = summarizer.summarize(content, style=summary_style)
        
        # Calculate compression percentage
        compression = (1 - result.summary_length / result.original_length) * 100
        
        # Save to database
        summary_id = db.save_summary(
            original_text=content,
            summary_text=result.summary,
            summary_style=summary_style,
            original_length=result.original_length,
            summary_length=result.summary_length,
            compression_rate=compression,
            model_used=result.model_used
        )
        
        # Return success response
        return jsonify({
            'success': True,
            'summary_id': summary_id,
            'summary': result.summary,
            'metadata': {
                'original_length': result.original_length,
                'summary_length': result.summary_length,
                'compression': f"{compression:.1f}%",
                'model_used': result.model_used,
                'timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'style': summary_style
            }
        })
    
    except InvalidContentError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid content: {str(e)}'
        }), 400
    
    except RateLimitError as e:
        return jsonify({
            'success': False,
            'error': f'Rate limit exceeded: {str(e)}'
        }), 429
    
    except AuthenticationError as e:
        return jsonify({
            'success': False,
            'error': f'Authentication error: {str(e)}'
        }), 401
    
    except ModelNotAvailableError as e:
        return jsonify({
            'success': False,
            'error': f'Model not available: {str(e)}'
        }), 503
    
    except NetworkError as e:
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
        }), 503
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


@app.route('/history')
def history():
    """Get summary history."""
    try:
        if db is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        style_filter = request.args.get('style', None)
        
        summaries = db.get_all_summaries(limit=limit, offset=offset, style_filter=style_filter)
        
        return jsonify({
            'success': True,
            'summaries': summaries,
            'count': len(summaries)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/history/<int:summary_id>')
def get_summary(summary_id):
    """Get a specific summary by ID."""
    try:
        if db is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        summary = db.get_summary(summary_id)
        
        if summary:
            return jsonify({'success': True, 'summary': summary})
        else:
            return jsonify({'success': False, 'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/history/<int:summary_id>', methods=['DELETE'])
def delete_summary(summary_id):
    """Delete a summary by ID."""
    try:
        if db is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        deleted = db.delete_summary(summary_id)
        
        if deleted:
            return jsonify({'success': True, 'message': 'Summary deleted'})
        else:
            return jsonify({'success': False, 'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/statistics')
def statistics():
    """Get summary statistics."""
    try:
        if db is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        stats = db.get_statistics()
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/search')
def search():
    """Search summaries."""
    try:
        if db is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        results = db.search_summaries(query)
        return jsonify({'success': True, 'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/export/<int:summary_id>/<format>')
def export_summary(summary_id, format):
    """Export a summary in various formats."""
    try:
        if db is None or exporter is None:
            return jsonify({'success': False, 'error': 'Export not available'}), 500
        
        # Get summary from database
        summary = db.get_summary(summary_id)
        if not summary:
            return jsonify({'success': False, 'error': 'Summary not found'}), 404
        
        # Prepare export data
        export_data = {
            'summary': summary['summary_text'],
            'original_text': summary['original_text'],
            'summary_style': summary['summary_style'],
            'original_length': summary['original_length'],
            'summary_length': summary['summary_length'],
            'compression': f"{summary['compression_rate']:.1f}%",
            'model_used': summary['model_used'],
            'timestamp': summary['created_at']
        }
        
        # Export based on format
        if format == 'pdf':
            buffer = exporter.export_to_pdf(export_data)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'summary_{summary_id}.pdf'
            )
        
        elif format == 'docx':
            buffer = exporter.export_to_word(export_data)
            return send_file(
                buffer,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=f'summary_{summary_id}.docx'
            )
        
        elif format == 'md':
            content = exporter.export_to_markdown(export_data)
            response = make_response(content)
            response.headers['Content-Type'] = 'text/markdown'
            response.headers['Content-Disposition'] = f'attachment; filename=summary_{summary_id}.md'
            return response
        
        elif format == 'txt':
            content = exporter.export_to_text(export_data)
            response = make_response(content)
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Content-Disposition'] = f'attachment; filename=summary_{summary_id}.txt'
            return response
        
        else:
            return jsonify({'success': False, 'error': 'Invalid export format'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'summarizer_initialized': summarizer is not None,
        'database_initialized': db is not None
    })


if __name__ == '__main__':
    # Run the Flask app
    print("\n" + "=" * 60)
    print("Content Summarizer Web UI")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    # Get port from environment variable (for deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
