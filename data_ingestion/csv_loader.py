"""
csv_loader.py

Loads a CSV file to build a mapping of CIK to a dict containing SICH and CONM values.
Example CSV columns:
    - cik
    - sich
    - conm
"""

import csv

class CSVLoader(object):
    """
    Responsible for loading a CSV that maps CIK to { "sich": <str>, "conm": <str> }.
    Example CSV columns:
        - cik
        - sich
        - conm
    """
    def __init__(self, csv_file_path):
        """
        Args:
            csv_file_path (str): Full path to the CSV file.
        """
        self.csv_file_path = csv_file_path

    def load_cik_sich_mapping(self):
        """
        Reads a CSV file and returns a dict mapping:
            CIK (str) -> { "sich": <SICH (str)>, "conm": <CONM (str)> }

        Returns:
            dict: A dictionary of the form:
                {
                  "123456": {"sich": "3711", "conm": "Some Company Inc"},
                  "234567": {"sich": "2834", "conm": "Another Company LLC"},
                  ...
                }
        """
        cik_to_sich = {}

        try:
            f = open(self.csv_file_path, "r", encoding="utf-8")
        except:
            print("Could not open CSV file at " + self.csv_file_path)
            return cik_to_sich  # empty if we can't open

        reader = csv.DictReader(f)
        for row in reader:
            # Convert the CIK to string and strip to avoid leading/trailing spaces
            cik_str = row["cik"].strip()
            try:
                # Convert to int then back to str to remove leading zeros or decimals
                cik_str = str(int(cik_str))
            except:
                # If conversion fails, just keep the original
                pass

            # Get the SICH and CONM columns; strip() them to clean whitespace
            sich_str = row.get("sich", "").strip()
            conm_str = row.get("conm", "").strip()

            # Only store the first entry if that is the desired behavior
            # (If you want the last one encountered, just remove the "if cik_str not in..." check)
            if cik_str not in cik_to_sich:
                cik_to_sich[cik_str] = {
                    "sich": sich_str,
                    "conm": conm_str
                }

        f.close()
        return cik_to_sich
