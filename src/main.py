#!/usr/bin/env python3
"""
ytcapt - Main Script Wrapper
"""

import sys
import traceback
from dotenv import load_dotenv
from script_reporter import ScriptReporter
from ytcapt import main as ytcapt_main

# Load environment variables
load_dotenv()

def main():
    """Main entry point with reporting for CLI"""
    sr = ScriptReporter("ytcapt")
    
    try:
        # Note: ytcapt_main handles its own argument parsing and printing
        # For full integration, we could refactor ytcapt.py to return results
        ytcapt_main()
        sr.success({"status": "completed"})
    except Exception:
        sr.fail(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
