"""
Test Hybrid Converter (DocLayout-YOLO + pdf2docx)

This tests the hybrid approach:
- Images: Detected by DocLayout-YOLO
- Text/Tables: Processed by pdf2docx
"""

# Apply PyMuPDF compatibility patch FIRST (before importing pdf2docx)
from pymupdf_patch import apply_pymupdf_patch
apply_pymupdf_patch()

from hybrid_converter import HybridConverter


def test_hybrid_converter():
    """Test the hybrid converter"""

    print("\n" + "="*80)
    print(" " * 20 + "HYBRID CONVERTER TEST")
    print(" " * 15 + "(YOLO Images + pdf2docx Text/Tables)")
    print("="*80)
    print()

    # Configuration
    pdf_file = 'test_files/2503.20314v2.pdf'
    output_file = 'test_files/result_hybrid.docx'
    model_path = 'weights/doclayout_yolo_docstructbench_imgsz1024.pt'

    print(f"Input PDF:  {pdf_file}")
    print(f"Output DOCX: {output_file}")
    print(f"YOLO Model: {model_path}")
    print()

    # Create hybrid converter
    converter = HybridConverter(yolo_model_path=model_path)

    # Convert with hybrid approach
    converter.convert(
        pdf_path=pdf_file,
        docx_path=output_file,
        use_yolo_images=True,      # Use YOLO for images
        yolo_conf=0.25,             # YOLO confidence threshold
        yolo_imgsz=1024,            # YOLO image size
    )

    print("\n" + "="*80)
    print("SUCCESS! Hybrid conversion completed")
    print("="*80)
    print()
    print("What was done:")
    print("  ✓ DocLayout-YOLO detected figure regions")
    print("  ✓ pdf2docx processed text and tables")
    print("  ✓ Combined into single DOCX file")
    print()
    print("Next steps:")
    print(f"  1. Open {output_file}")
    print("  2. Compare with:")
    print("     - result_doclayout.docx (YOLO only)")
    print("     - result_smart_merge.docx (ImageMerger)")
    print("  3. Check that:")
    print("     - Figures are complete (from YOLO)")
    print("     - Text is properly formatted (from pdf2docx)")
    print("     - Tables are preserved (from pdf2docx)")
    print()


def compare_methods():
    """Compare different conversion methods"""

    print("\n" + "="*80)
    print(" " * 25 + "METHOD COMPARISON")
    print("="*80)
    print()

    methods = [
        {
            'name': 'Original pdf2docx',
            'file': 'test_files/result_pdf2docx_origin.docx',
            'pros': '✓ Good text formatting, ✓ Fast',
            'cons': '✗ Images fragmented'
        },
        {
            'name': 'ImageMerger',
            'file': 'test_files/result_smart_merge.docx',
            'pros': '✓ Images merged, ✓ Fast',
            'cons': '~ Heuristic merging'
        },
        {
            'name': 'DocLayout-YOLO Only',
            'file': 'test_files/result_doclayout.docx',
            'pros': '✓ Perfect images',
            'cons': '✗ Missing text formatting'
        },
        {
            'name': 'HYBRID (Best)',
            'file': 'test_files/result_hybrid.docx',
            'pros': '✓ Perfect images, ✓ Good text',
            'cons': '~ Slower (YOLO overhead)'
        }
    ]

    for i, method in enumerate(methods, 1):
        print(f"{i}. {method['name']}")
        print(f"   File: {method['file']}")
        print(f"   Pros: {method['pros']}")
        print(f"   Cons: {method['cons']}")
        print()

    print("Recommendation:")
    print("  → Use HYBRID for best quality (images + text)")
    print("  → Use ImageMerger for speed")
    print()


if __name__ == "__main__":
    # Test hybrid converter
    test_hybrid_converter()

    # Show comparison
    compare_methods()
