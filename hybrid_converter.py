"""
Hybrid PDF to DOCX Converter
Combines DocLayout-YOLO (for images and formulas) + pdf2docx (for text/tables)

Strategy:
1. Use DocLayout-YOLO to detect figure and formula regions
2. Use UniMERNet to recognize formulas and convert to MathML
3. Use pdf2docx for text, tables, and other content
4. Replace pdf2docx's image extraction with YOLO-detected regions
"""

import os
import torch
from doclayout_yolo import YOLOv10
from pdf2docx import Converter
import fitz


class YOLORegionDetector:
    """DocLayout-YOLO region detector for pdf2docx integration (figures + formulas)"""

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

        # Cache for detected regions (page_num -> {'figures': [...], 'formulas': [...]})
        self.detected_regions = {}

        print(f"[YOLO] Model loaded successfully\n")

    def detect_page_regions(self, page, page_num):
        """
        Detect figure and formula regions in a PDF page

        Args:
            page: fitz.Page object
            page_num: Page number (0-indexed)

        Returns:
            dict: {'figures': [regions], 'formulas': [regions]}
                  Each region: {'bbox': [x0,y0,x1,y1], 'confidence': float}
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
        formulas = []

        if len(results) > 0 and hasattr(results[0], 'boxes'):
            for box in results[0].boxes:
                # Get class
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = self.model.names[cls_id]

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

                region_data = {
                    'bbox': pdf_bbox,
                    'confidence': float(box.conf[0].cpu().numpy())
                }

                # Categorize by type
                if class_name.lower() in ['figure', 'picture']:
                    figures.append(region_data)
                elif class_name.lower() in ['isolate_formula', 'formula']:
                    formulas.append(region_data)

        # Cache results
        regions = {'figures': figures, 'formulas': formulas}
        self.detected_regions[page_num] = regions

        if figures or formulas:
            print(f"[YOLO] Page {page_num + 1}: Detected {len(figures)} figures, {len(formulas)} formulas")

        return regions


class HybridConverter:
    """
    Hybrid PDF to DOCX Converter
    Uses DocLayout-YOLO for images and formulas, pdf2docx for everything else
    """

    def __init__(self, yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
                 unimernet_cfg_path="FreeTex/demo.yaml"):
        """
        Initialize hybrid converter

        Args:
            yolo_model_path: Path to DocLayout-YOLO model
            unimernet_cfg_path: Path to UniMERNet config file
        """
        self.yolo_detector = YOLORegionDetector(model_path=yolo_model_path)
        self.unimernet_cfg_path = unimernet_cfg_path
        self.formula_recognizer = None  # Lazy load UniMERNet
        self.formula_processor = None

    def _load_unimernet(self):
        """Lazy load UniMERNet model"""
        if self.formula_recognizer is not None:
            return

        print("[UniMERNet] Loading formula recognition model...")

        import sys
        import os

        # Save current directory
        original_dir = os.getcwd()

        # Change to FreeTex directory for model loading
        freetex_dir = os.path.join(os.path.dirname(__file__), 'FreeTex')
        os.chdir(freetex_dir)

        # Add FreeTex to path
        if freetex_dir not in sys.path:
            sys.path.insert(0, freetex_dir)

        try:
            import argparse
            import unimernet.tasks as tasks
            from unimernet.common.config import Config
            from unimernet.processors import load_processor

            # Setup model
            args = argparse.Namespace(cfg_path=os.path.basename(self.unimernet_cfg_path), options=None)
            cfg = Config(args)

            task = tasks.setup_task(cfg)
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            # Build and load model
            self.formula_recognizer = task.build_model(cfg).to(device)
            self.formula_recognizer.eval()

            # Load processor
            self.formula_processor = load_processor(
                "formula_image_eval",
                cfg.config.datasets.formula_rec_eval.vis_processor.eval,
            )

            print(f"[UniMERNet] Model loaded on {device}\n")

        finally:
            # Restore original directory
            os.chdir(original_dir)

    def _recognize_formula(self, page, bbox):
        """
        Recognize formula from PDF page region

        Args:
            page: fitz.Page object
            bbox: [x0, y0, x1, y1] coordinates

        Returns:
            str: LaTeX formula string
        """
        # Ensure UniMERNet is loaded
        self._load_unimernet()

        # Extract formula region as image
        rect = fitz.Rect(bbox)
        mat = fitz.Matrix(3.0, 3.0)  # Higher resolution for formula recognition
        pix = page.get_pixmap(matrix=mat, clip=rect)

        # Convert to PIL Image
        import io
        from PIL import Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data)).convert("RGB")

        # Process with UniMERNet
        device = next(self.formula_recognizer.parameters()).device
        image_tensor = self.formula_processor(img).unsqueeze(0).to(device)

        with torch.no_grad():
            output = self.formula_recognizer.generate({"image": image_tensor})

        latex_code = output["pred_str"][0]
        return latex_code

    def _latex_to_mathml(self, latex_code):
        """
        Convert LaTeX to MathML

        Args:
            latex_code: LaTeX string

        Returns:
            str: MathML string
        """
        try:
            from latex2mathml.converter import convert
            mathml = convert(latex_code)
            return mathml
        except Exception as e:
            print(f"[Warning] LaTeX to MathML conversion failed: {e}")
            print(f"  LaTeX: {latex_code}")
            return None

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
        print(f"  - Images & Formulas: {'DocLayout-YOLO + UniMERNet' if use_yolo else 'pdf2docx'}")
        print(f"  - Text/Tables: pdf2docx")
        print(f"{'='*80}\n")

        if use_yolo:
            # Pre-detect all figures and formulas with YOLO
            print("[YOLO] Pre-detecting figures and formulas in all pages...")
            pdf_doc = fitz.open(pdf_path)

            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                self.yolo_detector.detect_page_regions(page, page_num)

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

        # Insert formulas if any were detected
        if use_yolo:
            self._insert_formulas_to_docx(pdf_path, docx_path)

        print(f"\n{'='*80}")
        print(f"Conversion completed!")
        print(f"Output: {docx_path}")
        print(f"{'='*80}\n")

    def _insert_formulas_to_docx(self, pdf_path, docx_path):
        """
        Insert MathML formulas into the generated DOCX file

        Args:
            pdf_path: Original PDF file
            docx_path: Generated DOCX file
        """
        # Check if there are any formulas detected
        has_formulas = False
        for regions in self.yolo_detector.detected_regions.values():
            if regions.get('formulas'):
                has_formulas = True
                break

        if not has_formulas:
            return

        print("\n[Formula] Processing formulas...")

        # Open PDF
        pdf_doc = fitz.open(pdf_path)

        # Recognize all formulas
        formula_data = {}  # page_num -> [(bbox, latex, mathml), ...]

        for page_num, regions in self.yolo_detector.detected_regions.items():
            formulas = regions.get('formulas', [])
            if not formulas:
                continue

            page = pdf_doc[page_num]
            page_formulas = []

            for formula in formulas:
                bbox = formula['bbox']

                # Recognize formula
                print(f"[Formula] Page {page_num + 1}: Recognizing formula at {bbox}...")
                latex = self._recognize_formula(page, bbox)
                print(f"  LaTeX: {latex}")

                # Convert to MathML
                mathml = self._latex_to_mathml(latex)

                if mathml:
                    page_formulas.append({
                        'bbox': bbox,
                        'latex': latex,
                        'mathml': mathml
                    })
                    print(f"  ✓ Converted to MathML")
                else:
                    print(f"  ✗ MathML conversion failed")

            if page_formulas:
                formula_data[page_num] = page_formulas

        pdf_doc.close()

        # Insert formulas into DOCX
        if formula_data:
            print(f"\n[Formula] Inserting {sum(len(f) for f in formula_data.values())} formulas into DOCX...")
            self._insert_mathml_into_docx(docx_path, formula_data)
            print(f"[Formula] Formulas inserted successfully\n")

    def _insert_mathml_into_docx(self, docx_path, formula_data):
        """
        Insert MathML formulas into DOCX file

        Args:
            docx_path: Path to DOCX file
            formula_data: Dict of {page_num: [{'bbox': [...], 'latex': str, 'mathml': str}]}
        """
        from docx import Document

        # Open document
        doc = Document(docx_path)

        # For each page with formulas
        for page_num, formulas in sorted(formula_data.items()):
            # Find approximate location in document to insert formula
            # Since pdf2docx converts page by page, we can estimate position

            # For now, append formulas at the end of document
            # A more sophisticated approach would be to find the exact position based on bbox

            for formula_info in formulas:
                mathml = formula_info['mathml']
                latex = formula_info['latex']

                # Insert MathML as OMML (Office Math ML)
                try:
                    # Strip MathML declaration if present
                    if mathml.startswith('<?xml'):
                        mathml = mathml[mathml.index('?>') + 2:].strip()

                    # Create OMML element from MathML (returns a math run, not paragraph)
                    math_run = self._create_omml_from_mathml(mathml)

                    if math_run:
                        # Create a new paragraph and add the math run to it
                        paragraph = doc.add_paragraph()
                        paragraph._element.append(math_run)
                    else:
                        # Fallback: insert as plain text
                        doc.add_paragraph(f"[Formula: {latex}]")

                except Exception as e:
                    print(f"[Warning] Failed to insert formula: {e}")
                    # Fallback: insert as plain text
                    doc.add_paragraph(f"[Formula: {latex}]")

        # Save document
        doc.save(docx_path)

    def _create_omml_from_mathml(self, mathml):
        """
        Create OMML (Office Math ML) run element from MathML

        Note: This is a simplified conversion that creates a basic OMML structure.
        For full MathML→OMML conversion, consider using an XSLT transform.

        Args:
            mathml: MathML string

        Returns:
            OxmlElement (w:r with m:oMath) or None
        """
        from docx.oxml import parse_xml
        from lxml import etree

        try:
            # Parse the MathML
            mathml_tree = etree.fromstring(mathml.encode('utf-8'))

            # Extract the formula content (simplified approach)
            # Get text content from MathML for basic display
            formula_text = ''.join(mathml_tree.itertext())

            # Create OMML run with math zone
            # This creates a proper Word math run structure
            omml_xml = f'''
            <w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
                <m:oMath>
                    <m:r>
                        <w:rPr>
                            <w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>
                        </w:rPr>
                        <m:t>{formula_text}</m:t>
                    </m:r>
                </m:oMath>
            </w:r>
            '''

            omml_elem = parse_xml(omml_xml)
            return omml_elem

        except Exception as e:
            print(f"[Warning] Failed to create OMML: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _inject_yolo_to_pdf2docx(self, pdf_path):
        """
        Inject YOLO detected regions into pdf2docx's image extraction
        Also filter out text/shapes that overlap with YOLO detected regions

        This modifies pdf2docx's internal image extraction to use YOLO results
        """
        # Monkey-patch pdf2docx's ImagesExtractor
        from pdf2docx.image.ImagesExtractor import ImagesExtractor
        from pdf2docx.shape.Paths import Paths
        from pdf2docx.shape.Shapes import Shapes
        from pdf2docx.page.RawPageFitz import RawPageFitz

        # Save original methods
        original_extract_images = ImagesExtractor.extract_images
        original_paths_restore = Paths.restore
        original_shapes_restore = Shapes.restore
        original_to_shapes_and_images = Paths.to_shapes_and_images
        original_preprocess_text = RawPageFitz._preprocess_text

        yolo_detector = self.yolo_detector

        def _rect_overlap_ratio(rect1, rect2):
            """Calculate overlap ratio between two rectangles"""
            # Convert to fitz.Rect if needed
            r1 = fitz.Rect(rect1) if not isinstance(rect1, fitz.Rect) else rect1
            r2 = fitz.Rect(rect2) if not isinstance(rect2, fitz.Rect) else rect2

            # Get intersection
            intersection = r1 & r2
            if intersection.is_empty:
                return 0.0

            # Calculate areas
            intersection_area = intersection.width * intersection.height
            r1_area = r1.width * r1.height

            if r1_area == 0:
                return 0.0

            return intersection_area / r1_area

        def yolo_enhanced_extract_images(self, clip_image_res_ratio=3.0, **kwargs):
            """Enhanced image extraction using YOLO detections"""

            page = self._page
            page_num = page.number

            # Get YOLO detected figures for this page
            regions = yolo_detector.detected_regions.get(page_num, {})
            yolo_figures = regions.get('figures', [])

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

                print(f"[YOLO] Page {page_num + 1}: Using {len(images)} YOLO-detected images from extract_images()")
                return images
            else:
                # Fall back to original pdf2docx image extraction
                result = original_extract_images(self, clip_image_res_ratio, **kwargs)
                if result:
                    print(f"[Debug] Page {page_num + 1}: extract_images() returned {len(result)} images (no YOLO)")
                return result

        def yolo_filtered_preprocess_text(self, **settings):
            """Filter out text blocks that overlap with YOLO detected regions"""
            # Get page number
            page_num = self.page_engine.number
            regions = yolo_detector.detected_regions.get(page_num, {})
            yolo_figures = regions.get('figures', [])

            # Call original method to get all text blocks
            text_blocks = original_preprocess_text(self, **settings)

            # If no YOLO figures or formulas, return original result
            yolo_formulas = regions.get('formulas', [])
            if not yolo_figures and not yolo_formulas:
                return text_blocks

            # Convert YOLO regions to Rect list (both figures and formulas)
            yolo_rects = [fitz.Rect(fig['bbox']) for fig in yolo_figures]
            yolo_rects.extend([fitz.Rect(formula['bbox']) for formula in yolo_formulas])

            # Filter out text blocks that overlap with YOLO regions
            filtered_blocks = []
            filtered_count = 0
            for block in text_blocks:
                # Check if this is a text block (type 0) vs image block (type 1)
                if block.get('type') != 0:
                    filtered_blocks.append(block)
                    continue

                block_bbox = fitz.Rect(block['bbox'])
                overlaps = False
                for yolo_rect in yolo_rects:
                    overlap_ratio = _rect_overlap_ratio(block_bbox, yolo_rect)
                    if overlap_ratio > 0.5:  # More than 50% overlap
                        overlaps = True
                        filtered_count += 1
                        break

                if not overlaps:
                    filtered_blocks.append(block)

            if filtered_count > 0:
                print(f"[Filter] Page {page_num + 1}: Filtered {filtered_count} text blocks overlapping with YOLO regions")

            return filtered_blocks

        def yolo_filtered_paths_restore(self, raws:list):
            """Completely skip paths for pages with YOLO detections"""
            # Get page number
            page_num = getattr(self.parent, 'number', 0)
            regions = yolo_detector.detected_regions.get(page_num, {})
            yolo_figures = regions.get('figures', [])
            yolo_formulas = regions.get('formulas', [])

            # If page has YOLO detections (figures or formulas), skip all path processing
            if yolo_figures or yolo_formulas:
                print(f"[Filter] Page {page_num + 1}: Disabled all path processing (using YOLO only)")
                return self  # Return empty paths
            else:
                # No YOLO detections, use original method
                return original_paths_restore(self, raws)

        def yolo_filtered_shapes_restore(self, raws:list):
            """Filter out shapes that overlap with YOLO detected regions"""
            # Get page number
            page_num = getattr(self.parent, 'number', 0)
            regions = yolo_detector.detected_regions.get(page_num, {})
            yolo_figures = regions.get('figures', [])
            yolo_formulas = regions.get('formulas', [])

            # If no YOLO figures or formulas, use original method
            if not yolo_figures and not yolo_formulas:
                return original_shapes_restore(self, raws)

            # Convert YOLO regions to Rect list (both figures and formulas)
            yolo_rects = [fitz.Rect(fig['bbox']) for fig in yolo_figures]
            yolo_rects.extend([fitz.Rect(formula['bbox']) for formula in yolo_formulas])

            # Filter shapes
            from pdf2docx.shape.Shape import Stroke, Fill, Hyperlink
            self.reset()
            rect = (0, 0, self.parent.width, self.parent.height)
            filtered_count = 0

            for raw in raws:
                # Distinguish specified type by key like `start`, `end` and `uri` (same as original)
                if 'start' in raw:
                    shape = Stroke(raw)
                elif 'uri' in raw:
                    shape = Hyperlink(raw)
                else:
                    shape = Fill(raw)

                # Ignore shape out of page
                if not shape.bbox.intersects(rect):
                    continue

                # Check if shape overlaps with any YOLO region
                overlaps = False
                for yolo_rect in yolo_rects:
                    overlap_ratio = _rect_overlap_ratio(shape.bbox, yolo_rect)
                    if overlap_ratio > 0.9:  # More than 90% overlap (changed from 50%)
                        overlaps = True
                        filtered_count += 1
                        break

                if not overlaps:
                    self.append(shape)

            if filtered_count > 0:
                print(f"[Filter] Page {page_num + 1}: Filtered {filtered_count} overlapping shapes")

            return self

        def yolo_filtered_to_shapes_and_images(self,
                                               min_svg_gap_dx:float=15,
                                               min_svg_gap_dy:float=15,
                                               min_w:float=2,
                                               min_h:float=2,
                                               clip_image_res_ratio:float=3.0):
            """Completely disable SVG image generation for pages with YOLO detections"""
            # Get page number
            page_num = getattr(self.parent, 'number', 0)
            regions = yolo_detector.detected_regions.get(page_num, {})
            yolo_figures = regions.get('figures', [])
            yolo_formulas = regions.get('formulas', [])

            # If page has YOLO detections (figures or formulas), disable all SVG/Path image generation
            if yolo_figures or yolo_formulas:
                # Only generate shapes (for tables/text styles), NO images
                iso_shapes = []
                if self.is_iso_oriented:
                    iso_shapes.extend(self.to_shapes())

                print(f"[Filter] Page {page_num + 1}: Disabled SVG/Path image generation (using YOLO only)")
                return iso_shapes, []  # Return empty images list
            else:
                # No YOLO detections, use original method
                return original_to_shapes_and_images(
                    self, min_svg_gap_dx, min_svg_gap_dy, min_w, min_h, clip_image_res_ratio)

        # Apply monkey-patches
        ImagesExtractor.extract_images = yolo_enhanced_extract_images
        RawPageFitz._preprocess_text = yolo_filtered_preprocess_text
        Paths.restore = yolo_filtered_paths_restore
        Paths.to_shapes_and_images = yolo_filtered_to_shapes_and_images
        # Shapes.restore = yolo_filtered_shapes_restore  # Disabled: may interfere with table parsing


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
