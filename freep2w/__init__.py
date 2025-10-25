"""
FreeP2W - Free PDF to Word Converter
"""

__version__ = "1.0.0"

from .hybrid_converter import HybridConverter
from .cli import convert_pdf_to_docx

__all__ = ["HybridConverter", "convert_pdf_to_docx"]
