"""
metadata_extractor.py

Functions or classes for extracting metadata from 10-k form filenames.
"""

import os

class MetadataExtractor(object):
    """
    Extracts metadata (date, form_type, cik, accession_number, etc.) from filenames.
    Expects the filename pattern: date_formType_edgar_data_cik_accession.json
    Example: 20210101_10K_edgar_data_123456_0000123456.json
    """

    @staticmethod
    def extract_from_filename(filename):
        """
        Extracts metadata from the given filename based on a fixed naming convention.

        Args:
            filename (str): The filename (not a full path).

        Returns:
            dict: Dictionary containing 'date', 'form_type', 'cik', 'accession_number'.
        """
        parts = filename.split('_')
        if len(parts) < 6:
            raise ValueError("Filename '{}' does not match expected format.".format(filename))

        date = parts[0][:4]
        form_type = parts[1]
        # parts[2] is 'edgar', parts[3] is 'data'
        cik = parts[4]
        accession_number_raw = parts[5]
        accession_number = os.path.splitext(accession_number_raw)[0]

        return {
            "date": int(date),
            "form_type": form_type,
            "cik": cik,
            "accession_number": accession_number
        }
