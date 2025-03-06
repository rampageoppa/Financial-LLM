"""
report_loader.py

High-level class for loading multiple JSON reports from a directory,
extracting metadata, cleaning text, and returning Document objects.
"""

import os
import json

# LangChain-specific import
from langchain.schema import Document

# Local module imports
from data_ingestion.data_cleaner import DataCleaner
from data_ingestion.metadata_extractor import MetadataExtractor

class ReportLoader(object):
    """
    Handles directory scanning and JSON file parsing to create Document objects.
    """

    def __init__(self, reports_directory, cik_to_sich=None):
        """
        Args:
            reports_directory (str): Path to the directory containing the .json reports.
            cik_to_sich (dict, optional): Mapping of CIK -> SICH, if available.
        """
        self.reports_directory = reports_directory
        if cik_to_sich is None:
            self.cik_to_sich = {}
        else:
            self.cik_to_sich = cik_to_sich

    def list_json_reports(self):
        """
        Recursively scans the `reports_directory` for .json files.

        Returns:
            list: A list of full file paths to each .json file.
        """
        file_paths = []
        for root, dirs, files in os.walk(self.reports_directory):
            for filename in files:
                if filename.endswith('.json'):
                    file_paths.append(os.path.join(root, filename))
        return file_paths

    def load_document_from_file(self, file_path):
        """
        Loads and cleans each JSON report, returning a list of Document objects.

        Args:
            file_path (str): The path to a single .json file.

        Returns:
            list: A list of LangChain `Document` objects.
        """
        documents = []
        filename = os.path.basename(file_path)

        # Extract metadata from filename
        try:
            file_metadata = MetadataExtractor.extract_from_filename(filename)
        except ValueError as e:
            print("Metadata extraction error:", str(e))
            return documents  # Return empty list if filename format is invalid

        date = file_metadata.get("date", "9999")

        # Grab the CIK from extracted metadata
        cik = file_metadata.get("cik", "")

        # Initialize metadata variables for SICH and company name
        sich = None
        company_name = None

        # Attempt to retrieve both 'sich' and 'conm' if available
        if cik in self.cik_to_sich:
            mapping = self.cik_to_sich[cik]  # This is a dict {"sich": ..., "conm": ...}
            sich = mapping.get("sich")
            company_name = mapping.get("conm")

        # If the CSV didn't have a company name, fallback:
        if not company_name:
            company_name = "Company with CIK " + cik

        # Load JSON data
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            print("Error decoding JSON from " + file_path)
            return documents

        # Each JSON file might contain multiple sections
        for section_key, section_text in data.items():
            cleaned_text = DataCleaner.clean_content(section_text)
            if not cleaned_text:
                continue

            metadata = {
                "file_name": filename,
                "section_title": section_key,
                "company_name": company_name,
                "cik": cik,
                "date": date
            }

            # Merge the extracted file metadata
            metadata.update(file_metadata)

            # Add SICH if available
            if sich is not None:
                metadata["sich"] = sich

            doc = Document(
                page_content=cleaned_text,
                metadata=metadata
            )
            documents.append(doc)

        return documents

    def load_all_documents(self, desired_sections=None):
        """
        Scans the directory, loads all .json files, and returns a combined list of Documents.
        Optionally filters only the desired sections (e.g., ["Item 1", "Item 7"]).

        Args:
            desired_sections (list): A list of section titles to keep. If None, all sections are kept.

        Returns:
            list: List of Document objects with optional section filtering.
        """
        all_documents = []
        file_paths = self.list_json_reports()
        print("Found " + str(len(file_paths)) + " JSON files in " + self.reports_directory)

        idx = 0
        for file_path in file_paths:
            idx += 1
            docs = self.load_document_from_file(file_path)

            # Filter by desired_sections if provided
            if desired_sections:
                filtered_docs = []
                for d in docs:
                    section_title = d.metadata.get("section_title")
                    if section_title in desired_sections:
                        filtered_docs.append(d)
                docs = filtered_docs

            all_documents.extend(docs)

            # Simple progress reporting
            if idx % 50 == 0:
                print("Processed " + str(idx) + " files...")

        print("Total loaded documents: " + str(len(all_documents)))
        return all_documents
