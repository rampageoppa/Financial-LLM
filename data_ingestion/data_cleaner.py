"""
data_cleaner.py

Contains functions for cleaning or preprocessing text,
such as removing page numbers and trimming whitespace.
"""

import re

class DataCleaner:
    """
    Provides static methods to clean text content.
    """

    @staticmethod
    def clean_content(text: str) -> str:
        """
        Cleans up the given text by removing page numbers,
        excessive newlines, and extra whitespace.

        Args:
            text (str): The raw text to clean.

        Returns:
            str: A cleaned version of the input text.
        """
        # Remove patterns like '\n3 ' (page numbers)
        text = re.sub(r'\n\d+\s*', ' ', text)
        # Replace newlines with spaces
        text = text.replace('\n', ' ').strip()
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
