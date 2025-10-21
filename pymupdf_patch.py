"""
PyMuPDF Compatibility Patch for pdf2docx

Fixes Rect.get_area() compatibility issue between different PyMuPDF versions
"""

import fitz


def _get_rect_area(rect):
    """Get area of a Rect object, compatible with both old and new PyMuPDF versions"""
    # Use new PyMuPDF properties if available
    if hasattr(rect, 'width') and hasattr(rect, 'height'):
        return rect.width * rect.height
    else:
        # Calculate manually from coordinates
        return abs((rect.x1 - rect.x0) * (rect.y1 - rect.y0))


# Monkey-patch Rect class
if not hasattr(fitz.Rect, 'get_area'):
    fitz.Rect.get_area = _get_rect_area


def apply_pymupdf_patch():
    """Apply PyMuPDF compatibility patches"""
    # Ensure get_area() method exists
    if not hasattr(fitz.Rect, 'get_area'):
        fitz.Rect.get_area = _get_rect_area
    print("[Patch] Applied PyMuPDF compatibility patch")


if __name__ == "__main__":
    # Test the patch
    apply_pymupdf_patch()

    rect = fitz.Rect(0, 0, 100, 50)
    print(f"Rect: {rect}")
    print(f"Area: {rect.get_area()}")
    print("Patch works!")
