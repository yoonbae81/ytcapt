import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import ytcapt

class TestYTCapt(unittest.TestCase):
    """Test cases for ytcapt.py core logic"""

    def test_parse_video_id_standard(self):
        """Test parsing standard YouTube URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = ytcapt._parse_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")

    def test_parse_video_id_short(self):
        """Test parsing shortened YouTube URL"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = ytcapt._parse_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")

    def test_parse_video_id_invalid(self):
        """Test parsing invalid URL"""
        url = "https://example.com"
        video_id = ytcapt._parse_video_id(url)
        self.assertIsNone(video_id)

if __name__ == '__main__':
    unittest.main()
