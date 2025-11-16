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
from contextlib import redirect_stderr
from io import StringIO
from bottle import Bottle, request, template, run, static_file, TEMPLATE_PATH


# --- (1) Try importing required libraries ---
try:
    # yt-dlp is imported here for internal use (fast info check)
    # but the main logic relies on importing ytcapt.py
    import yt_dlp
    from yt_dlp.utils import YoutubeDLError
except ImportError:
    # This check is less critical here since ytcapt.py does the main check
    pass 

# --- Import core logic from ytcapt ---
try:
    from ytcapt import (
        retrieve_subtitle_file,
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
    Maintains single spaces and removes leading/trailing dots/spaces.
    """
    if not filename:
        return "Untitled"
    
    # 1. 시스템 파일명 금지 문자 (Windows/Linux)를 공백으로 대체
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    safe_name = re.sub(invalid_chars, ' ', filename)
    
    # 2. 이모지 및 파일명에 혼란을 줄 수 있는 기타 특수 기호를 제거
    safe_name = re.sub(r'[^\w\s\.-]', ' ', safe_name)
    
    # 3. 연속된 공백을 단일 공백으로 압축
    safe_name = re.sub(r'\s+', ' ', safe_name)
    
    # 4. 파일명 앞뒤의 공백 또는 점(.)을 제거하여 확장자 앞의 문제를 방지
    safe_name = safe_name.strip(' .')
    
    if not safe_name:
        return "Untitled File"
        
    # 5. 최대 길이 제한 (200자)
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
        
    return safe_name

def process_url(url: str, lang: str) -> dict:
    """
    Main logic to check URL type and process it.
    Returns a dictionary indicating the result type and data.
    """
    
    # Step 1: Check if it's a playlist (fast, no download)
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'ignoreerrors': True,
    }
    
    info = None
    with redirect_stderr(StringIO()):
        # Use yt_dlp directly for the fast info check
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                # Rely on ytcapt.py's exception structure for clean message
                raise SubtitleError(f"Failed to check URL: {e}")

    if info is None:
        raise DownloadError(
            "Video information extraction failed: Request likely blocked by YouTube "
            "due to bot detection or access restrictions (e.g., private/restricted video, "
            "or requiring sign-in)."
        )

    video_type = info.get('_type', 'video')

    # Step 2: Handle Playlists
    if video_type == 'playlist':
        entries = []
        for entry in info.get('entries', []):
            if entry:
                entries.append({
                    'title': entry.get('title', 'Unknown Title'),
                    'url': entry.get('url', '#')
                })
        return {
            'type': 'playlist',
            'title': info.get('title', 'Playlist'),
            'entries': entries,
            'lang': lang
        }

    # Step 3: Handle Single Video
    # retrieve_subtitle_file handles cache, download logic, and raises clean SubtitleError
    srt_filepath, video_info = retrieve_subtitle_file(url, lang, force_dl=False)
    lines = extract_pure_text_lines(srt_filepath)
    final_text = refine_sentences(lines, lang)
    
    # Step 4: Construct output text for DOWNLOAD FILE (with header)
    video_title_full = video_info.get('title', 'Untitled')
    
    # Download file content includes header (Title, URL, Blank Line, Text)
    output_text_for_download = (
        f"{video_title_full}\n"
        f"{url}\n"
        f"\n"
        f"{final_text}"
    )
    
    # Step 5: Save for download
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
        'text_content': final_text, # 웹페이지 textarea에는 순수 자막만 표시
        'download_url': f'download/{filename}'
    }

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
    run(app, host='localhost', port=8080, debug=True, reloader=True)
