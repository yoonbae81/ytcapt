#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ytcapt.py: A simplified CLI tool to download, cache, and refine subtitles
from a single YouTube video URL using youtube_transcript_api.
"""

import sys
import os
import time
import re
import importlib
import tempfile
import argparse
from typing import Optional, List

# --- (1) Library Imports ---
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, InvalidVideoId
except ImportError:
    print("Error: 'youtube-transcript-api' is not installed. Please run: pip install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)

# --- (2) Constants and Configuration ---
CACHE_DIR = os.path.join(tempfile.gettempdir(), "ytcapt_cache")
CACHE_DURATION_SECONDS = 7 * 24 * 60 * 60  # 7 days
TRANSCRIPT_FILENAME_SUFFIX = ".txt"  # Use TXT for caching pure text lines

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
    """Raised when the transcript file cannot be parsed."""
    pass

# --- (4) Core Logic Functions ---

def _parse_video_id(url: str) -> Optional[str]:
    """Parses a YouTube URL to find the video ID."""
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match and len(match.group(1)) == 11 else None

def get_transcript_cache_path(video_id: str, lang: str) -> str:
    """Generates the filepath for the transcript TXT cache file."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    base_filename = f"{video_id}.{lang}"
    return os.path.join(CACHE_DIR, f"{base_filename}{TRANSCRIPT_FILENAME_SUFFIX}")

def get_transcript_lines(video_id: str, lang: str, force_dl: bool) -> List[str]:
    """
    Fetches transcript lines from cache or downloads them.
    Saves the extracted text lines to a .txt cache file.
    Returns a list of subtitle text lines.
    """
    cache_path = get_transcript_cache_path(video_id, lang)

    # 1. Check cache (unless forcing download)
    if not force_dl and os.path.exists(cache_path):
        try:
            if (time.time() - os.path.getmtime(cache_path)) > CACHE_DURATION_SECONDS:
                os.remove(cache_path)
            else:
                print("Cache hit. Using cached subtitle.", file=sys.stderr)
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read().splitlines()
        except OSError:
            pass  # Ignore errors and proceed to download

    # 2. If no cache or expired, download
    print("Cache miss or force-dl. Downloading subtitle...", file=sys.stderr)
    try:
        api = YouTubeTranscriptApi()
        fetched_data = api.fetch(video_id, [lang])

        # Extract text from the 'snippets' attribute of the FetchedTranscript object
        snippets = fetched_data.snippets
        lines = [snippet.text.strip() for snippet in snippets if snippet.text]
        
        # Save plain text to cache
        text_content = "\n".join(lines)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
            
        return lines

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, InvalidVideoId) as e:
        raise DownloadError(f"Could not retrieve transcript for video ID '{video_id}': {e}")
    except Exception as e:
        raise DownloadError(f"An unexpected error occurred during transcript download: {e}")

def _refine_default_sentences(lines: list[str]) -> str:
    """Default/English logic: Join all, then split by punctuation."""
    full_text = " ".join(lines)
    sentences = re.split(r'([.?!])', full_text)
    
    processed_sentences = []
    i = 0
    while i < len(sentences) - 1:
        sentence = (sentences[i] + sentences[i+1]).strip()
        if sentence:
            processed_sentences.append(sentence)
        i += 2
    
    if i < len(sentences) and sentences[i].strip():
        processed_sentences.append(sentences[i].strip())

    return "\n\n".join(processed_sentences)

def refine_sentences(lines: list[str], lang: str) -> str:
    """
    Refines a list of text lines into coherent sentences.
    Dynamically loads a refinement module based on the language.
    """
    safe_lang = re.sub(r'[^a-zA-Z0-9_]', '', lang)
    module_name = f"src.refiners.refine_{safe_lang}"

    try:
        refiner_module = importlib.import_module(module_name)
        return refiner_module.refine_sentences(lines)
    except ImportError:
        return _refine_default_sentences(lines)
    except Exception as e:
        raise ParsingError(f"An error occurred in the '{module_name}' module: {e}")

# --- (5) CLI Execution Logic ---

def main():
    """Main function to run the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Download, cache, and refine subtitles for a single YouTube video.",
        epilog="Example: python src/ytcapt.py \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\" -l en"
    )
    
    parser.add_argument("url", type=str, help="The full video URL to process.")
    parser.add_argument("-l", "--lang", type=str, default="ko", help="Language code for subtitles (e.g., 'ko', 'en').")
    parser.add_argument("-f", "--force-dl", action="store_true", help="Force download, ignoring any existing cache.")
    
    args = parser.parse_args()

    try:
        video_id = _parse_video_id(args.url)
        if not video_id:
            raise InvalidUrlError("Could not parse a valid YouTube video ID from the URL.")

        # Get transcript lines from cache or download
        lines = get_transcript_lines(video_id, args.lang, args.force_dl)
        
        if not lines:
            raise ParsingError("No text could be extracted from the subtitle data.")
            
        final_text = refine_sentences(lines, args.lang)
        print(final_text)

    except SubtitleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected critical error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # This allows the script to find the 'src' module when run from the root directory
    if 'src' not in sys.path[0] and 'src' not in os.getcwd():
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    main()
