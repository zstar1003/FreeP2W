"""
Batch PDF to DOCX conversion using DocLayout-YOLO

Usage:
    python batch_convert.py --input-dir pdfs/ --output-dir outputs/
"""

import os
import argparse
from doclayout_converter import DocLayoutYOLOConverter


def batch_convert(input_dir, output_dir, model_path, imgsz=1024, conf=0.25):
    """Batch convert PDFs to DOCX"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    print(f"\nFound {len(pdf_files)} PDF files")
    print("="*80)

    # Create converter
    converter = DocLayoutYOLOConverter(model_path=model_path)

    # Process each PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(input_dir, pdf_file)
        docx_file = pdf_file.replace('.pdf', '_doclayout.docx')
        docx_path = os.path.join(output_dir, docx_file)

        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file}")

        try:
            converter.convert(
                pdf_path=pdf_path,
                docx_path=docx_path,
                imgsz=imgsz,
                conf=conf
            )
            print(f"✓ Success: {docx_file}")

        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "="*80)
    print("Batch conversion completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True, help='Input directory with PDF files')
    parser.add_argument('--output-dir', default='outputs', help='Output directory for DOCX files')
    parser.add_argument('--model', default='weights/doclayout_yolo_docstructbench_imgsz1024.pt')
    parser.add_argument('--imgsz', type=int, default=1024)
    parser.add_argument('--conf', type=float, default=0.25)

    args = parser.parse_args()

    batch_convert(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        model_path=args.model,
        imgsz=args.imgsz,
        conf=args.conf
    )
