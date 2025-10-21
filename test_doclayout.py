"""
Test DocLayout-YOLO Converter

Quick test script for the hybrid converter
"""

from doclayout_converter import DocLayoutYOLOConverter


def test_doclayout_converter():
    """Test the DocLayout-YOLO converter"""

    print("\n" + "="*80)
    print(" " * 20 + "DOCLAYOUT-YOLO CONVERTER TEST")
    print("="*80)
    print()

    # Configuration
    pdf_file = 'test_files/2503.20314v2.pdf'
    output_file = 'test_files/result_doclayout.docx'
    model_path = 'weights/doclayout_yolo_docstructbench_imgsz1024.pt'

    print(f"Input PDF:  {pdf_file}")
    print(f"Output DOCX: {output_file}")
    print(f"Model: {model_path}")
    print()

    # Create converter
    converter = DocLayoutYOLOConverter(model_path=model_path)

    # Convert
    converter.convert(
        pdf_path=pdf_file,
        docx_path=output_file,
        imgsz=1024,          # YOLO image size
        conf=0.25,           # Confidence threshold
        dpi=150,             # DPI for layout detection
        image_quality=4.0    # Image extraction quality
    )

    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print()
    print("Next steps:")
    print(f"  1. Open {output_file} to check results")
    print("  2. Verify that figures are extracted as complete images")
    print("  3. Check that text is still readable")
    print()


if __name__ == "__main__":
    test_doclayout_converter()
