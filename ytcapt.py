#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ytcapt.py: A CLI tool to download, cache, and refine auto-generated subtitles
from video URLs.
"""

import sys
import os
import time
import argparse
import re
from contextlib import redirect_stderr
from io import StringIO
import tempfile
import json
import importlib 
# from urllib.error import HTTPError # Removed, as it is wrapped by yt-dlp

# --- (1) Try importing required libraries ---
try:
    import yt_dlp
    from yt_dlp.utils import YoutubeDLError

except ImportError:
    print(
        "Error: Required library 'yt-dlp' is not installed.",
        file=sys.stderr
    )
    print(
        "Please install it using: pip install yt-dlp",
        file=sys.stderr
    )
    sys.exit(1)

# --- (2) Constants and Configuration ---
CACHE_DIR = os.path.join(tempfile.gettempdir(), "ytcapt_cache")
CACHE_DURATION_SECONDS = 7 * 24 * 60 * 60  # 7 days
# Metadata filename to store video title
METADATA_FILENAME = "metadata.json"


# --- (3) Custom Exceptions ---
class SubtitleError(Exception):
    """Base exception for this module."""
    pass

class InvalidUrlError(SubtitleError):
    """Raised when the URL is invalid or video ID cannot be extracted."""
    pass

class DownloadError(SubtitleError):
    """Raised when download fails or no suitable captions are found."""
    pass

class ParsingError(SubtitleError):
    """Raised when the SRT file cannot be parsed."""
    pass


# --- (4) Core Logic Functions ---

def _parse_video_id(url: str) -> str | None:
    """
    Parses a YouTube URL to find the video ID.
    Handles various YouTube URL formats and validates length.
    """
    # Regex for standard watch?v= format and youtu.be/ format (11 chars)
    match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", url)
    if match and len(match.group(1)) == 11:
        return match.group(1)
        
    return None

def get_cache_filepaths(video_id: str, lang: str) -> tuple[str, str]:
    """
    Generates filepaths for the SRT file and the metadata file.
    Ensures the cache directory exists.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    srt_filename = f"{video_id}.{lang}.srt"
    meta_filename = f"{video_id}.{METADATA_FILENAME}"
    return (
        os.path.join(CACHE_DIR, srt_filename),
        os.path.join(CACHE_DIR, meta_filename)
    )

def check_cache(srt_filepath: str, meta_filepath: str) -> bool:
    """
    Checks if a valid, non-expired cache file AND its metadata exist.
    """
    if not os.path.exists(srt_filepath) or not os.path.exists(meta_filepath):
        return False

    # Check file age based on the SRT file
    try:
        file_mod_time = os.path.getmtime(srt_filepath)
        current_time = time.time()
        age_seconds = current_time - file_mod_time

        if age_seconds > CACHE_DURATION_SECONDS:
            # Cache is expired, delete both files
            try:
                os.remove(srt_filepath)
                os.remove(meta_filepath)
            except OSError:
                pass
            return False
    except OSError:
        # If we can't get mtime, treat as expired/invalid
        return False
    
    return True

def retrieve_subtitle_file(url: str, lang: str, force_dl: bool) -> tuple[str, dict]:
    """
    Gets the SRT filepath. Caches based on a simple parsed video ID.
    Only accesses network if cache is missed.
    Returns (srt_filepath, info_dict)
    """
    
    # --- Step 1: Parse URL for simple ID ---
    parsed_id = _parse_video_id(url)
    if not parsed_id:
        raise InvalidUrlError("Could not parse a valid YouTube video ID from the URL. "
                              "Only standard YouTube links are supported.")

    # --- Step 2: Check Cache ---
    srt_filepath, meta_filepath = get_cache_filepaths(parsed_id, lang)
    
    if not force_dl and check_cache(srt_filepath, meta_filepath):
        # Cache Hit: Read title from metadata and return
        try:
            with open(meta_filepath, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Construct info object from cached data
            cached_info = {
                "id": parsed_id,
                "title": metadata.get("title", f"Cached Video ({parsed_id})")
            }
            return srt_filepath, cached_info
        except Exception:
            # If reading metadata fails, treat as cache miss and force download
            pass 

    # --- Step 3: Cache Miss or Force Download (Access Network) ---
    f = StringIO()
    info = None
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'sublangs': [lang],
    }
    
    with redirect_stderr(f):
        try:
            # --- Request 1: Get Info ---
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # --- Request 2: Download SRT ---
            captions_dict = info.get('automatic_captions', {})
            if lang not in captions_dict:
                raise DownloadError(f"No auto-captions found for language '{lang}'.")
            
            srt_url = None
            for format_info in captions_dict[lang]:
                if format_info.get('ext') == 'srt':
                    srt_url = format_info.get('url')
                    break
            
            if not srt_url:
                raise DownloadError(f"Could not find SRT format URL for '{lang}'.")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                with ydl.urlopen(srt_url) as response:
                    srt_data = response.read()
                    
                    # Save SRT data
                    with open(srt_filepath, 'wb') as f_cache:
                        f_cache.write(srt_data)
                        
                    # Save Metadata (Title)
                    title = info.get('title', 'Untitled')
                    metadata = {"title": title}
                    with open(meta_filepath, 'w', encoding='utf-8') as f_meta:
                        json.dump(metadata, f_meta)

        except YoutubeDLError as e:
            error_message = str(e)
            
            # Check for bot-detection related errors
            if "confirm you’re not a bot" in error_message or \
               "Please sign in" in error_message:
                raise DownloadError(
                    f"Access Denied: YouTube blocked the request, requiring sign-in "
                    f"to confirm you are not a bot. Try passing cookies via the ydl_opts"
                )
            
            # Check for 429 error (Too Many Requests)
            if "429" in error_message or "Too Many Requests" in error_message:
                raise DownloadError(
                    f"HTTP Error 429: The requested language ('{lang}') is likely unavailable "
                    "for download from your current region/IP due to YouTube restrictions."
                )
            # Catch all other yt-dlp related errors
            raise DownloadError(error_message)
        
        except Exception as e:
            if isinstance(e, SubtitleError): 
                raise
            # Fallback for unexpected, non-yt-dlp/non-HTTP errors
            raise DownloadError(f"An unexpected error occurred during the download phase: {e}")

    # --- Step 4: Final Check ---
    if not os.path.exists(srt_filepath):
         raise DownloadError(f"Download was reported successful, but file not found at: {srt_filepath}")
    
    # On cache miss, return the *real* info object
    return srt_filepath, info


def extract_pure_text_lines(srt_filepath: str) -> list[str]:
    """
    Parses the SRT file, extracts all text captions, and removes
    consecutive duplicates.
    """
    try:
        with open(srt_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        # Use srt_filepath which is defined in this function scope
        raise ParsingError(f"Failed to read SRT file: {e}\nFile: {srt_filepath}")

    blocks = re.split(r'\r?\n\r?\n', content.strip())
    lines = []
    last_line = None
    
    for block in blocks:
        block_lines = block.strip().splitlines()
        if len(block_lines) < 3:
            continue
        text_content = " ".join(block_lines[2:])
        text = text_content.strip().replace(">>", "").strip()
        
        if text and text != last_line:
            lines.append(text)
            last_line = text
    
    return lines


def _refine_default_sentences(lines: list[str]) -> str:
    """
    Default/English logic: Join all, then split by punctuation.
    """
    full_text = " ".join(lines)
    sentences = re.split(r'([.?!])', full_text)
    
    processed_sentences = []
    i = 0
    while i < len(sentences) - 1:
        if sentences[i].strip():
            processed_sentences.append(sentences[i].strip() + sentences[i+1])
        i += 2
    
    if i < len(sentences) and sentences[i].strip():
        processed_sentences.append(sentences[i].strip() + ".")

    return "\n\n".join(processed_sentences)


def refine_sentences(lines: list[str], lang: str) -> str:
    """
    Refines a list of text lines into coherent sentences/paragraphs.
    Dynamically loads the refinement module based on language.
    """
    
    safe_lang = re.sub(r'[^a-zA-Z0-9_]', '', lang)
    module_name = f"refiners.refine_{safe_lang}"

    try:
        refiner_module = importlib.import_module(module_name)
        return refiner_module.refine_sentences(lines)
        
    except ImportError:
        return _refine_default_sentences(lines)
    except Exception as e:
        raise ParsingError(
            f"An error occurred in the '{module_name}' module: {e}"
        )


# --- (5) CLI Execution Logic ---

def main():
    """
    Main function to run the CLI tool.
    Parses arguments and orchestrates the download/refining process.
    """
    parser = argparse.ArgumentParser(
        description="Download, cache, and refine auto-generated subtitles.",
        epilog="Example: python ytcapt.py \"[URL]\" -l ko"
    )
    
    parser.add_argument(
        "url",
        type=str,
        help="The full video URL to process."
    )
    parser.add_argument(
        "-l", "--lang",
        type=str,
        default="ko",
        help="Language code for the subtitles (e.g., 'ko', 'en'). Default: 'ko'."
    )
    parser.add_argument(
        "-f", "--force-dl",
        action="store_true",
        help="Force download, ignoring any existing cache."
    )
    
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        srt_filepath, _ = retrieve_subtitle_file(args.url, args.lang, args.force_dl)
        lines = extract_pure_text_lines(srt_filepath)
        final_text = refine_sentences(lines, args.lang)
        print(final_text)

    except SubtitleError as e:
        # Print the custom, user-friendly error message
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected critical error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()