# YT Caption Downloader

Automatically downloads, refines, and structures auto-generated captions from online videos.

## 📝 Overview

This project provides both a command-line interface (CLI) and a web application interface (using [Bottle](https://bottlepy.org)) to download and process auto-generated subtitles from video platforms. The core function is to transform fragmented, time-stamped subtitle lines into coherent, readable paragraphs (refinement).

## Core Architecture

The project maintains a flexible architecture:

`ytcapt.py`: Contains the core logic for fetching, caching, and refining subtitles. It acts as a standalone CLI tool and a library module for app.py.

`app.py`: A lightweight [Bottle](https://bottlepy.org) application that imports the logic from `ytcapt.py` to provide a user-friendly web interface.

`refiners/`: A package for language-specific refinement rules (currently only `refine_ko.py` and default English logic).

## ✨ Key Features

- Web Interface (Bottle): Offers a simple, responsive, and auto-theming CSS framework ([Pico](https://picocss.com)) for easy use.

- Subtitle Refinement: Merges fragmented lines into full sentences and paragraphs, making the text suitable for reading or analysis.

- Targeted Download: Ensures high compatibility by strictly targeting auto-generated captions, which are available on almost all videos, maximizing the chance of successful extraction.

- Playlist Handling: Accepts video playlist URLs, offering a selection menu to process individual videos within the list.

- Error Handling: Provides user-friendly error messages, particularly for "HTTP 429: Too Many Requests," which indicates a likely region/IP restriction issue by the video platform.

- Caching: Caches downloaded SRT files for 7 days based on video ID to reduce unnecessary network requests and processing time.

- Download Header: Downloaded .txt files include the original video title and URL in the first two lines for easy source tracking.

- Robust File Naming: Sanitizes video titles to create clean, file-system-safe download names while preserving spaces.

## 🛠️ Setup and Installation

This program requires Python 3.9+ and the following libraries.

Clone Repository:
```
git clone https://github.com/yoonbae81/ytcapt
cd ytcapt/src
```

Install Dependencies:
A requirements.txt file containing yt-dlp and bottle is required.

```
pip install -r ../requirements.txt
```

## ⚙️ Usage

### A. Web Application (Recommended)

The web app allows easy access to all features via a browser.

1. Run the Server:
```
python app.py
```

2. Access the Application:
Open your browser to http://localhost:8080/.

3. Operation:

    - Enter a Video or Playlist URL.

    - Select the target language (Korean or English).

    - The app will display the refined text or a playlist selection menu.

    - The download button saves the content with a safe filename derived from the video title.

### B. Command-Line Interface (CLI)

Use `ytcapt.py` directly for script automation or batch processing.

1. Basic Usage (Korean):
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX"
```


2. Specify Language (English):
Use the --lang or -l option.
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX" -l en
```


3. Force Download (Ignore Cache):
Use the --force-dl or -f option.
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX" -f
```


## 📂 Project Structure

```
/ytcapt/src
|
|-- app.py             # Bottle web server application
|-- ytcapt.py          # Core logic module and CLI script
|
|-- refiners/          # Language-specific refinement package
|   |-- __init__.py    # Makes it a Python package
|   +-- refine_ko.py   # Korean sentence refinement rules
|
+-- views/             # Bottle templates (Pico CSS applied)
    |-- home.tpl       # URL and Language input form
    |-- result.tpl     # Display refined text and download links
    +-- playlist.tpl   # List of videos for playlist selection
```
