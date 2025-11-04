"""
OSPAC data processing pipeline.
Generates policy data from SPDX licenses using LLM analysis.
"""

from ospac.pipeline.spdx_processor import SPDXProcessor
from ospac.pipeline.llm_analyzer import LicenseAnalyzer
from ospac.pipeline.data_generator import PolicyDataGenerator

__all__ = [
    "SPDXProcessor",
    "LicenseAnalyzer",
    "PolicyDataGenerator",
]