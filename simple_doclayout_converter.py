"""
Simplified DocLayout-YOLO Converter (No PyMuPDF dependency)

Uses:
- DocLayout-YOLO for layout detection
- pdf2image for PDF to image conversion
- python-docx for DOCX generation
"""

import os
import torch
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt
from doclayout_yolo import YOLOv10
from pdf2image import convert_from_path
import io


class SimpleDocLayoutConverter:
    """PDF to DOCX converter using DocLayout-YOLO (without PyMuPDF)"""

    def __init__(self, model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt"):
        """Initialize converter with DocLayout-YOLO model"""
        print(f"[INFO] Loading DocLayout-YOLO model...")

        # Auto select device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[INFO] Using device: {self.device}")

        # Load model
        self.model = YOLOv10(model_path)
        print(f"[INFO] Model loaded successfully")

    def convert(self, pdf_path, docx_path, imgsz=1024, conf=0.25, dpi=150):
        """
        Convert PDF to DOCX using layout detection

        Args:
            pdf_path: Path to input PDF
            docx_path: Path to output DOCX
            imgsz: Image size for YOLO (default: 1024)
            conf: Confidence threshold (default: 0.25)
            dpi: DPI for PDF rendering (default: 150)
        """
        print(f"\n{'='*80}")
        print(f"Converting: {pdf_path}")
        print(f"{'='*80}\n")

        # Convert PDF to images
        print("[INFO] Converting PDF pages to images...")
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"[INFO] Loaded {len(images)} pages")

        # Create DOCX
        docx_doc = Document()

        # Process each page
        for page_num, page_img in enumerate(images):
            print(f"\n{'-'*80}")
            print(f"Processing Page {page_num + 1}/{len(images)}")
            print(f"{'-'*80}")

            # Save page as temp image for YOLO
            temp_img_path = f"_temp_page_{page_num}.png"
            page_img.save(temp_img_path)

            # Detect layout with DocLayout-YOLO
            layout_regions = self._detect_layout(temp_img_path, page_img, imgsz, conf)

            # Clean up temp file
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

            # Sort regions by reading order
            layout_regions.sort(key=lambda r: (r['bbox'][1], r['bbox'][0]))

            # Process each region
            for i, region in enumerate(layout_regions, 1):
                region_type = region['type']
                bbox = region['bbox']
                confidence = region['confidence']

                print(f"  [{i}/{len(layout_regions)}] {region_type} (conf: {confidence:.2f})")

                if region_type.lower() in ['figure', 'picture']:
                    # Extract and insert figure
                    self._insert_figure_region(page_img, bbox, docx_doc)

                elif region_type.lower() in ['table']:
                    # Extract table as image
                    print(f"      [Table] Extracting as image")
                    self._insert_figure_region(page_img, bbox, docx_doc)

                # Note: Text extraction is skipped for now (would need OCR)

            # Add page break
            if page_num < len(images) - 1:
                docx_doc.add_page_break()

        # Save DOCX
        docx_doc.save(docx_path)

        print(f"\n{'='*80}")
        print(f"Conversion completed!")
        print(f"Output: {docx_path}")
        print(f"{'='*80}\n")

    def _detect_layout(self, img_path, pil_img, imgsz, conf):
        """Detect layout regions using DocLayout-YOLO"""

        # Run YOLO detection
        det_res = self.model.predict(
            img_path,
            imgsz=imgsz,
            conf=conf,
            device=self.device,
        )

        # Parse results
        regions = []

        if len(det_res) > 0 and hasattr(det_res[0], 'boxes'):
            boxes = det_res[0].boxes

            for box in boxes:
                # Get bbox coordinates (in pixels)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Get class and confidence
                cls_id = int(box.cls[0].cpu().numpy())
                conf_score = float(box.conf[0].cpu().numpy())

                # Get class name
                class_name = self.model.names[cls_id]

                regions.append({
                    'type': class_name,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf_score
                })

        print(f"  Detected {len(regions)} regions")

        # Show summary by type
        type_counts = {}
        for r in regions:
            type_counts[r['type']] = type_counts.get(r['type'], 0) + 1

        for rtype, count in sorted(type_counts.items()):
            print(f"    - {rtype}: {count}")

        return regions

    def _insert_figure_region(self, page_img, bbox, docx_doc):
        """Extract figure region from page image and insert into DOCX"""

        x1, y1, x2, y2 = bbox

        # Crop figure from page image
        fig_img = page_img.crop((x1, y1, x2, y2))

        # Convert to bytes
        img_buffer = io.BytesIO()
        fig_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Calculate width in inches
        max_width = 6.0  # inches
        width_px = x2 - x1
        width_inches = width_px / 150.0  # Assuming 150 DPI

        if width_inches > max_width:
            width_inches = max_width

        # Insert into DOCX
        try:
            docx_doc.add_picture(img_buffer, width=Inches(width_inches))
            print(f"      [Figure] Inserted: {width_px} x {y2-y1} px")
        except Exception as e:
            print(f"      [Error] Failed to insert figure: {e}")


def main():
    """Test the converter"""
    import argparse

    parser = argparse.ArgumentParser(description='PDF to DOCX using DocLayout-YOLO (Simple Version)')
    parser.add_argument('--pdf', required=True, help='Input PDF file')
    parser.add_argument('--output', help='Output DOCX file')
    parser.add_argument('--model', default='weights/doclayout_yolo_docstructbench_imgsz1024.pt')
    parser.add_argument('--imgsz', type=int, default=1024)
    parser.add_argument('--conf', type=float, default=0.25)
    parser.add_argument('--dpi', type=int, default=150)

    args = parser.parse_args()

    if args.output is None:
        args.output = args.pdf.replace('.pdf', '_simple_doclayout.docx')

    # Create converter
    converter = SimpleDocLayoutConverter(model_path=args.model)

    # Convert
    converter.convert(
        pdf_path=args.pdf,
        docx_path=args.output,
        imgsz=args.imgsz,
        conf=args.conf,
        dpi=args.dpi
    )


if __name__ == "__main__":
    main()
