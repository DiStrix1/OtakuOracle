# tests/test_recommend.py

import os
import sys
import json
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.recommend_service import get_recommendations, load_manga_data


class TestRecommendService(unittest.TestCase):
    """Test cases for the recommendation service."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [
            {
                "title": "Naruto", 
                "description": "A ninja's journey to become Hokage.",
                "genres": ["Action", "Adventure"],
                "themes": ["Martial Arts"],
                "image_url": "https://example.com/naruto.jpg"
            },
            {
                "title": "One Piece", 
                "description": "Pirate crew sails to find the One Piece.",
                "genres": ["Action", "Adventure"],
                "themes": [],
                "image_url": "https://example.com/onepiece.jpg"
            },
            {
                "title": "Bleach", 
                "description": "Teen gains powers to fight evil spirits.",
                "genres": ["Action", "Supernatural"],
                "themes": [],
                "image_url": "https://example.com/bleach.jpg"
            },
            {
                "title": "Attack on Titan", 
                "description": "Humans fight for survival against Titans.",
                "genres": ["Action", "Drama"],
                "themes": ["Gore"],
                "image_url": "https://example.com/aot.jpg"
            },
            {
                "title": "Death Note", 
                "description": "A notebook grants power to kill.",
                "genres": ["Supernatural", "Thriller"],
                "themes": ["Psychological"],
                "image_url": "https://example.com/deathnote.jpg"
            },
        ]

    @patch('app.services.recommend_service.load_manga_data')
    def test_get_recommendations_success(self, mock_load_data):
        """Test successful recommendation retrieval."""
        # Mock the load_manga_data function to return test data
        mock_load_data.return_value = self.test_data
        
        # Test with a valid manga title
        result = get_recommendations("Naruto")
        
        # Verify we got recommendations
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        
        # We should have recommendations (up to 4 since we only have 5 manga total)
        self.assertTrue(len(result) > 0)
        self.assertTrue(len(result) <= 4)
        
        # Check structure of recommendations
        for rec in result:
            self.assertIn("title", rec)
            self.assertIn("score", rec)
            self.assertIn("genres", rec)
            self.assertIn("themes", rec)
            self.assertIn("image_url", rec)

    @patch('app.services.recommend_service.load_manga_data')
    def test_get_recommendations_partial_match(self, mock_load_data):
        """Test that recommendations work with partial title matching."""
        mock_load_data.return_value = self.test_data
        
        # Test with a partial title
        result = get_recommendations("Nar")  # Should match "Naruto"
        
        # Verify we got recommendations
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    @patch('app.services.recommend_service.load_manga_data')
    def test_get_recommendations_not_found(self, mock_load_data):
        """Test recommendation for non-existent manga."""
        mock_load_data.return_value = self.test_data
        
        # Test with an invalid manga title
        result = get_recommendations("Non-existent Manga")
        
        # Should return None for not found
        self.assertIsNone(result)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([{"title": "Test Manga"}]))
    @patch('pathlib.Path.resolve')
    @patch('pathlib.Path.exists')
    def test_load_manga_data(self, mock_exists, mock_resolve, mock_file):
        """Test loading manga data from file."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock path resolution
        mock_path = Path("/fake/path")
        mock_resolve.return_value = mock_path
        
        # Call the function
        result = load_manga_data()
        
        # Verify the result
        self.assertEqual(result, [{"title": "Test Manga"}])


if __name__ == "__main__":
    unittest.main()
