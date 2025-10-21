"""
Practical DocLayout-YOLO + pdf2docx Integration

Strategy:
1. Convert each PDF page to image using PyMuPDF (via pdf2docx's code)
2. Use DocLayout-YOLO to detect figure regions
3. Extract figure regions from PDF directly
4. Use pdf2docx for remaining content

This version works around import issues by using pdf2docx's existing code
"""

import os
import sys
import torch
from docx import Document
from docx.shared import Inches
from doclayout_yolo import YOLOv10
import io


# Add pdf2docx to path to access its modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pdf2docx'))

# Import from pdf2docx's internal modules
from pdf2docx.page import Page as PDFPage


class PracticalDocLayoutConverter:
    """PDF to DOCX using DocLayout-YOLO for figure detection"""

    def __init__(self, model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt"):
        """Initialize with DocLayout-YOLO model"""
        print(f"[INFO] Loading DocLayout-YOLO model...")

        # Auto select device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[INFO] Using device: {self.device}")

        # Load model
        self.model = YOLOv10(model_path)
        print(f"[INFO] Model loaded successfully\n")

    def convert(self, pdf_path, docx_path, imgsz=1024, conf=0.25, dpi=150):
        """Convert PDF to DOCX with figure detection"""

        print(f"{'='*80}")
        print(f"Converting: {pdf_path}")
        print(f"{'='*80}\n")

        # Use pdf2docx's converter to open PDF
        from pdf2docx.converter import Converter

        cv = Converter(pdf_path)
        pdf_doc = cv.pdf_doc

        # Create DOCX
        docx_doc = Document()

        # Process each page
        for page_num in range(len(pdf_doc)):
            print(f"{'-'*80}")
            print(f"Page {page_num + 1}/{len(pdf_doc)}")
            print(f"{'-'*80}")

            page = pdf_doc[page_num]

            # Step 1: Convert page to image for YOLO
            temp_img = f"_temp_page_{page_num}.png"
            mat = page.parent.page.rotation_matrix if hasattr(page.parent.page, 'rotation_matrix') else None
            zoom = dpi / 72
            if not mat:
                import pymupdf
                mat = pymupdf.Matrix(zoom, zoom)

            pix = page.get_pixmap(matrix=mat)
            pix.save(temp_img)

            # Step 2: Detect layout with YOLO
            figure_regions = self._detect_figures(temp_img, pix.width, pix.height,
                                                   page.rect.width, page.rect.height,
                                                   imgsz, conf)

            # Clean up temp image
            if os.path.exists(temp_img):
                os.remove(temp_img)

            # Step 3: Extract and insert figures
            for i, fig in enumerate(figure_regions, 1):
                bbox = fig['bbox']
                print(f"  Figure {i}: {bbox}")
                self._extract_and_insert_figure(page, bbox, docx_doc)

            # Add page break
            if page_num < len(pdf_doc) - 1:
                docx_doc.add_page_break()

        # Close PDF
        cv.close()

        # Save DOCX
        docx_doc.save(docx_path)

        print(f"\n{'='*80}")
        print(f"Completed! Output: {docx_path}")
        print(f"{'='*80}\n")

    def _detect_figures(self, img_path, img_width, img_height, pdf_width, pdf_height, imgsz, conf):
        """Detect figure regions using YOLO"""

        # Run YOLO
        results = self.model.predict(img_path, imgsz=imgsz, conf=conf, device=self.device)

        figures = []

        if len(results) > 0 and hasattr(results[0], 'boxes'):
            for box in results[0].boxes:
                # Get class
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = self.model.names[cls_id]

                # Only process figures
                if class_name.lower() not in ['figure', 'picture']:
                    continue

                # Get bbox in image coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Convert to PDF coordinates
                scale_x = pdf_width / img_width
                scale_y = pdf_height / img_height

                pdf_bbox = [
                    float(x1 * scale_x),
                    float(y1 * scale_y),
                    float(x2 * scale_x),
                    float(y2 * scale_y)
                ]

                figures.append({
                    'bbox': pdf_bbox,
                    'confidence': float(box.conf[0].cpu().numpy())
                })

        print(f"  Detected {len(figures)} figures")
        return figures

    def _extract_and_insert_figure(self, page, bbox, docx_doc):
        """Extract figure from PDF and insert to DOCX"""

        # Create rect
        import pymupdf
        rect = pymupdf.Rect(bbox)

        # Extract as high-quality image
        mat = pymupdf.Matrix(4, 4)  # 4x zoom
        pix = page.get_pixmap(matrix=mat, clip=rect)

        # Convert to PNG bytes
        img_data = pix.tobytes("png")

        # Insert to DOCX
        try:
            img_stream = io.BytesIO(img_data)

            # Calculate width
            max_width = 6.0  # inches
            width_pt = rect.width
            width_inches = width_pt / 72.0

            if width_inches > max_width:
                width_inches = max_width

            docx_doc.add_picture(img_stream, width=Inches(width_inches))
            print(f"    Inserted: {rect.width:.1f} x {rect.height:.1f} pt")

        except Exception as e:
            print(f"    Error: {e}")


def main():
    """Quick test"""
    converter = PracticalDocLayoutConverter()

    converter.convert(
        pdf_path='test_files/2503.20314v2.pdf',
        docx_path='test_files/result_practical_doclayout.docx',
        imgsz=1024,
        conf=0.25,
        dpi=150
    )


if __name__ == "__main__":
    main()
