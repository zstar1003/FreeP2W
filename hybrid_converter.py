"""
Hybrid PDF to DOCX Converter
Combines DocLayout-YOLO (for images) + pdf2docx (for text/tables)

Strategy:
1. Use DocLayout-YOLO to detect figure regions
2. Use pdf2docx for text, tables, and other content
3. Replace pdf2docx's image extraction with YOLO-detected regions
"""

import os
import torch
from doclayout_yolo import YOLOv10
from pdf2docx import Converter
import fitz


class YOLOImageDetector:
    """DocLayout-YOLO image detector for pdf2docx integration"""

    def __init__(self, model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
                 imgsz=1024, conf=0.25, dpi=150):
        """
        Initialize YOLO detector

        Args:
            model_path: Path to YOLO model
            imgsz: Image size for detection
            conf: Confidence threshold
            dpi: DPI for PDF rendering
        """
        print(f"[YOLO] Loading DocLayout-YOLO model...")

        # Auto select device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[YOLO] Using device: {self.device}")

        # Load model
        self.model = YOLOv10(model_path)
        self.imgsz = imgsz
        self.conf = conf
        self.dpi = dpi

        # Cache for detected regions (page_num -> [regions])
        self.detected_regions = {}

        print(f"[YOLO] Model loaded successfully\n")

    def detect_page_figures(self, page, page_num):
        """
        Detect figure regions in a PDF page

        Args:
            page: fitz.Page object
            page_num: Page number (0-indexed)

        Returns:
            list: Figure regions [{'bbox': [x0,y0,x1,y1], 'conf': float}, ...]
        """
        # Check cache
        if page_num in self.detected_regions:
            return self.detected_regions[page_num]

        # Convert page to image
        mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        # Save temp image
        temp_img = f"_temp_yolo_page_{page_num}.png"
        pix.save(temp_img)

        # Run YOLO detection
        results = self.model.predict(
            temp_img,
            imgsz=self.imgsz,
            conf=self.conf,
            device=self.device,
            verbose=False  # Suppress YOLO output
        )

        # Clean up temp file
        if os.path.exists(temp_img):
            os.remove(temp_img)

        # Parse results
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
                scale_x = page.rect.width / pix.width
                scale_y = page.rect.height / pix.height

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

        # Cache results
        self.detected_regions[page_num] = figures

        if figures:
            print(f"[YOLO] Page {page_num + 1}: Detected {len(figures)} figures")

        return figures


class HybridConverter:
    """
    Hybrid PDF to DOCX Converter
    Uses DocLayout-YOLO for images, pdf2docx for everything else
    """

    def __init__(self, yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt"):
        """Initialize hybrid converter"""
        self.yolo_detector = YOLOImageDetector(model_path=yolo_model_path)

    def convert(self, pdf_path, docx_path, **kwargs):
        """
        Convert PDF to DOCX with hybrid approach

        Args:
            pdf_path: Input PDF file
            docx_path: Output DOCX file
            **kwargs: Additional parameters for pdf2docx

        Supported kwargs:
            - use_yolo_images: bool (default True) - Use YOLO for image detection
            - yolo_conf: float (default 0.25) - YOLO confidence threshold
            - yolo_imgsz: int (default 1024) - YOLO image size
            - ... (other pdf2docx parameters)
        """
        use_yolo = kwargs.pop('use_yolo_images', True)

        # Update YOLO parameters if provided
        if 'yolo_conf' in kwargs:
            self.yolo_detector.conf = kwargs.pop('yolo_conf')
        if 'yolo_imgsz' in kwargs:
            self.yolo_detector.imgsz = kwargs.pop('yolo_imgsz')

        print(f"\n{'='*80}")
        print(f"Hybrid Conversion: {pdf_path}")
        print(f"  - Images: {'DocLayout-YOLO' if use_yolo else 'pdf2docx'}")
        print(f"  - Text/Tables: pdf2docx")
        print(f"{'='*80}\n")

        if use_yolo:
            # Pre-detect all figures with YOLO
            print("[YOLO] Pre-detecting figures in all pages...")
            pdf_doc = fitz.open(pdf_path)

            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                self.yolo_detector.detect_page_figures(page, page_num)

            pdf_doc.close()
            print()

            # Inject YOLO detector into pdf2docx
            self._inject_yolo_to_pdf2docx(pdf_path)

        # Convert with pdf2docx
        print("[pdf2docx] Converting with pdf2docx...")
        cv = Converter(pdf_path)

        # Set default parameters for better quality
        default_params = {
            'start': 0,
            'end': None,
        }
        default_params.update(kwargs)

        cv.convert(docx_path, **default_params)
        cv.close()

        print(f"\n{'='*80}")
        print(f"Conversion completed!")
        print(f"Output: {docx_path}")
        print(f"{'='*80}\n")

    def _inject_yolo_to_pdf2docx(self, pdf_path):
        """
        Inject YOLO detected regions into pdf2docx's image extraction

        This modifies pdf2docx's internal image extraction to use YOLO results
        """
        # Monkey-patch pdf2docx's ImagesExtractor
        from pdf2docx.image.ImagesExtractor import ImagesExtractor

        # Save original extract_images method
        original_extract_images = ImagesExtractor.extract_images

        yolo_detector = self.yolo_detector

        def yolo_enhanced_extract_images(self, clip_image_res_ratio=3.0, **kwargs):
            """Enhanced image extraction using YOLO detections"""

            page = self._page
            page_num = page.number

            # Get YOLO detected figures for this page
            yolo_figures = yolo_detector.detected_regions.get(page_num, [])

            if yolo_figures:
                # Use YOLO detections
                images = []
                for fig in yolo_figures:
                    bbox = fig['bbox']
                    rect = fitz.Rect(bbox)

                    # Extract image from PDF
                    mat = fitz.Matrix(clip_image_res_ratio, clip_image_res_ratio)
                    pix = page.get_pixmap(matrix=mat, clip=rect)

                    # Convert to pdf2docx format
                    if pix.colorspace.n > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    raw_dict = {
                        "type": 1,  # BlockType.IMAGE
                        "bbox": tuple(bbox),
                        "width": pix.width,
                        "height": pix.height,
                        "image": pix.tobytes(),
                    }

                    images.append(raw_dict)

                print(f"[YOLO] Page {page_num + 1}: Using {len(images)} YOLO-detected images")
                return images
            else:
                # Fall back to original pdf2docx image extraction
                return original_extract_images(self, clip_image_res_ratio, **kwargs)

        # Apply monkey-patch
        ImagesExtractor.extract_images = yolo_enhanced_extract_images


def main():
    """Test the hybrid converter"""
    import argparse

    parser = argparse.ArgumentParser(description='Hybrid PDF to DOCX Converter')
    parser.add_argument('--pdf', required=True, help='Input PDF file')
    parser.add_argument('--output', help='Output DOCX file (default: input_hybrid.docx)')
    parser.add_argument('--yolo-model', default='weights/doclayout_yolo_docstructbench_imgsz1024.pt')
    parser.add_argument('--yolo-conf', type=float, default=0.25, help='YOLO confidence threshold')
    parser.add_argument('--yolo-imgsz', type=int, default=1024, help='YOLO image size')
    parser.add_argument('--no-yolo', action='store_true', help='Disable YOLO, use pdf2docx only')

    args = parser.parse_args()

    # Set default output path
    if args.output is None:
        args.output = args.pdf.replace('.pdf', '_hybrid.docx')

    # Create converter
    converter = HybridConverter(yolo_model_path=args.yolo_model)

    # Convert
    converter.convert(
        pdf_path=args.pdf,
        docx_path=args.output,
        use_yolo_images=not args.no_yolo,
        yolo_conf=args.yolo_conf,
        yolo_imgsz=args.yolo_imgsz
    )


if __name__ == "__main__":
    main()
