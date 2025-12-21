#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py: Bottle web application for ytcapt.
Refactored to work with the new, simplified ytcapt.py module.
"""

import sys
import os
import re
import tempfile
from bottle import Bottle, request, template, run, static_file, TEMPLATE_PATH, redirect

# --- (1) Import core logic from the new ytcapt ---
try:
    from ytcapt import (
        _parse_video_id,
        get_transcript_lines,
        get_video_title,
        refine_sentences,
        SubtitleError,
        InvalidUrlError,
        DownloadError,
        ParsingError
    )
except ImportError:
    print("Error: 'ytcapt.py' not found.", file=sys.stderr)
    print("Please ensure 'ytcapt.py' is in the same directory as 'app.py'.", file=sys.stderr)
    sys.exit(1)

# --- (2) Constants and Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH.insert(0, os.path.join(SCRIPT_DIR, 'views'))
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "ytcapt_downloads")
BASE_URL = '/ytcapt'  # Base URL prefix for all routes

# --- (3) Helper Functions ---

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be a safe filename.
    """
    if not filename:
        return "Untitled"
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]' # Corrected escape for backslash
    safe_name = re.sub(invalid_chars, ' ', filename)
    safe_name = re.sub(r'[^\w\s\.-]', ' ', safe_name)
    safe_name = re.sub(r'\s+', ' ', safe_name).strip(' .')
    if not safe_name:
        return "Untitled File"
    return safe_name[:200]

def process_url(url: str, lang: str) -> dict:
    """
    Main logic to process a single video URL using the new ytcapt module.
    """
    # Step 1: Parse video ID from URL.
    video_id = _parse_video_id(url)
    if not video_id:
        raise InvalidUrlError("Could not parse a valid YouTube video ID from the URL.")

    # Step 2: Get video title.
    video_title = get_video_title(video_id)
    if not video_title:
        video_title = f"Video ID - {video_id}"

    # Step 3: Get transcript lines. This function handles caching and downloading.
    lines = get_transcript_lines(video_id, lang, force_dl=False)
    if not lines:
        raise ParsingError("No text could be extracted from the subtitle data.")

    # Step 4: Refine the transcript lines into sentences.
    final_text = refine_sentences(lines, lang)

    # Step 5: Prepare data for display and download.
    output_text_for_download = (
        f"{video_title}\n"
        f"{url}\n"
        f"\n"
        f"{final_text}"
    )
    
    safe_title = sanitize_filename(video_title)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    filename = f"{safe_title}.{lang}.txt"
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output_text_for_download)
    except Exception as e:
        raise SubtitleError(f"Failed to save temporary file: {e}")
        
    # Step 5: Return all necessary data for the template.
    return {
        'type': 'video',  # Only single videos are supported now
        'title': video_title,
        'text_content': final_text,
        'download_url': f'download/{filename}'
    }

# --- (4) Bottle Routes ---

app = Bottle()

@app.route('/')
def root_redirect():
    """Redirect root to base URL."""
    return redirect(f'{BASE_URL}/')

@app.route(BASE_URL)
def baseurl_redirect():
    """Redirect /ytcapt to /ytcapt/ (with trailing slash)."""
    return redirect(f'{BASE_URL}/')

@app.route(f'{BASE_URL}/', method=['GET', 'POST'])
def index():
    """
    Main route. Handles GET (with or without params) and POST.
    """
    if request.method == 'POST':
        url = request.forms.get('url', '').strip()
        lang = request.forms.get('lang', 'ko').strip()
    else: # GET request
        url = request.query.get('url', '').strip()
        lang = request.query.get('lang', 'ko').strip()
        
    if not url:
        return template('home.tpl', url='', lang=lang, error=None, baseurl=BASE_URL)

    try:
        result_data = process_url(url, lang)
        
        # Since only 'video' type is supported, we only need to handle that.
        return template('result.tpl', 
            title=result_data['title'],
            text_content=result_data['text_content'],
            download_url=result_data['download_url'],
            baseurl=BASE_URL
        )
            
    except SubtitleError as e:
        # Pass the custom, user-friendly error message directly to the template.
        return template('home.tpl', url=url, lang=lang, error=str(e), baseurl=BASE_URL)
    except Exception as e:
        # Catch any other unexpected errors.
        return template('home.tpl', url=url, lang=lang, error=f"An unexpected error occurred: {e}", baseurl=BASE_URL)

@app.route(f'{BASE_URL}/download/<filename:path>')
def download(filename):
    """
    Serves the generated text file for download.
    """
    return static_file(filename, root=DOWNLOAD_DIR, download=filename)

@app.route(f'{BASE_URL}/static/<filename:path>')
def server_static(filename):
    """
    Serves static CSS/JS files (if any).
    """
    return static_file(filename, root=os.path.join(SCRIPT_DIR, 'static'))

# --- (5) Run Server ---
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ytcapt web application')
    parser.add_argument('--port', type=int, default=8000, help='Port number to run the server on (default: 8000)')
    parser.add_argument('--production', action='store_true', help='Run in production mode with optimizations')
    args = parser.parse_args()
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Enable template caching in production
    if args.production:
        from bottle import TEMPLATES
        TEMPLATES.clear()  # Clear any cached templates
        # Run with production settings
        run(app, host='0.0.0.0', port=args.port, debug=False, reloader=False, server='auto')
    else:
        # Development mode
        run(app, host='0.0.0.0', port=args.port, debug=True, reloader=True)

