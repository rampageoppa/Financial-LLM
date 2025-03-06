"""
data_ingestion package.

Provides classes and functions for loading, cleaning, and extracting metadata
from CSV and JSON reports.
"""

__all__ = ["CSVLoader", "DataCleaner", "MetadataExtractor", "ReportLoader"]

# Re-export the main classes/functions so users can do:
#   from data_ingestion import CSVLoader
# instead of
#   from data_ingestion.csv_loader import CSVLoader

from .csv_loader import CSVLoader
from .data_cleaner import DataCleaner
from .metadata_extractor import MetadataExtractor
from .report_loader import ReportLoader
