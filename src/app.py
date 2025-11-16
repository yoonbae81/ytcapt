#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py: Bottle web application for ytcapt.
Integrates yt-dlp processing and subtitle refinement logic.
"""

import sys
import os
import re
import tempfile
from bottle import Bottle, request, template, run, static_file, TEMPLATE_PATH


# --- (1) Try importing required libraries ---
try:
    # yt-dlp is imported here for internal use (fast info check)
    # but the main logic relies on importing ytcapt.py
    pass
except ImportError:
    # This check is less critical here since ytcapt.py does the main check
    pass 

# --- Import core logic from ytcapt ---
try:
    from ytcapt import (
        _parse_video_id,
        check_and_get_srt_cache,
        extract_video_info,
        download_and_cache_subtitle,
        extract_pure_text_lines,
        refine_sentences,
        SubtitleError,
        InvalidUrlError,
        DownloadError,
        ParsingError
    )
except ImportError:
    print(
        "Error: 'ytcapt.py' not found.",
        file=sys.stderr
    )
    print(
        "Please ensure 'ytcapt.py' is in the same directory as 'app.py'.",
        file=sys.stderr
    )
    sys.exit(1) 


# --- (2) Constants and Configuration ---

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH.insert(0, os.path.join(SCRIPT_DIR, 'views'))
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "ytcapt_downloads")

# --- (3) Helper Functions ---

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be a safe filename for Windows/macOS/Linux.
    """
    if not filename:
        return "Untitled"
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    safe_name = re.sub(invalid_chars, ' ', filename)
    safe_name = re.sub(r'[^\w\s\.-]', ' ', safe_name)
    safe_name = re.sub(r'\s+', ' ', safe_name).strip(' .')
    if not safe_name:
        return "Untitled File"
    return safe_name[:200]

def _process_single_video(url: str, lang: str, srt_filepath: str, video_info: dict) -> dict:
    """
    Processes a single video given the SRT file path and video info.
    This is the final step for both cached and newly downloaded videos.
    """
    lines = extract_pure_text_lines(srt_filepath)
    final_text = refine_sentences(lines, lang)
    
    video_title_full = video_info.get('title', 'Untitled')
    
    output_text_for_download = (
        f"{video_title_full}\n"
        f"{url}\n"
        f"\n"
        f"{final_text}"
    )
    
    safe_title = sanitize_filename(video_title_full)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    filename = f"{safe_title}.{lang}.txt"
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output_text_for_download)
    except Exception as e:
        raise SubtitleError(f"Failed to save temporary file: {e}")
        
    return {
        'type': 'video',
        'title': video_title_full,
        'text_content': final_text,
        'download_url': f'download/{filename}'
    }

def process_url(url: str, lang: str) -> dict:
    """
    Main logic to check URL type and process it, now with a cache-first approach.
    """
    # --- Step 1: Fast-path for cached single videos ---
    video_id = _parse_video_id(url)
    if video_id:
        srt_filepath, video_info = check_and_get_srt_cache(video_id, lang)
        if srt_filepath and video_info:
            # Cache Hit! Process and return immediately.
            return _process_single_video(url, lang, srt_filepath, video_info)

    # --- Step 2: Cache Miss or Playlist - Go to network ---
    video_info = extract_video_info(url, force_dl=False)

    if not video_info:
        raise DownloadError(
            "Video information extraction failed. The URL may be private, invalid, or restricted."
        )

    video_type = video_info.get('_type', 'video')

    # --- Step 3: Handle Playlists ---
    if video_type == 'playlist':
        entries = []
        for entry in video_info.get('entries', []):
            if entry:
                entries.append({
                    'title': entry.get('title', 'Unknown Title'),
                    'url': entry.get('url', '#')
                })
        return {
            'type': 'playlist',
            'title': video_info.get('title', 'Playlist'),
            'entries': entries,
            'lang': lang
        }

    # --- Step 4: Handle newly fetched Single Video ---
    srt_filepath = download_and_cache_subtitle(video_info, lang)
    return _process_single_video(url, lang, srt_filepath, video_info)

# --- (4) Bottle Routes ---

app = Bottle()

@app.route('/', method=['GET', 'POST'])
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
        return template('home.tpl', url='', lang=lang, error=None)

    try:
        result_data = process_url(url, lang)
        
        if result_data['type'] == 'video':
            return template('result.tpl', 
                title=result_data['title'],
                text_content=result_data['text_content'],
                download_url=result_data['download_url']
            )
        elif result_data['type'] == 'playlist':
            return template('playlist.tpl',
                title=result_data['title'],
                entries=result_data['entries'],
                lang=result_data['lang']
            )
            
    except Exception as e:
        # Pass the message from the raised exception (SubtitleError) directly to the template.
        return template('home.tpl', url=url, lang=lang, error=str(e))

@app.route('/download/<filename:path>')
def download(filename):
    """
    Serves the generated text file for download.
    """
    return static_file(filename, root=DOWNLOAD_DIR, download=filename)

@app.route('/static/<filename:path>')
def server_static(filename):
    """
    Serves static CSS/JS files (if any).
    """
    return static_file(filename, root=os.path.join(SCRIPT_DIR, 'static'))

# --- (5) Run Server ---
if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    run(app, host='0.0.0.0', port=8080, debug=True, reloader=True)
