"""
Analyze text blocks near formulas to find missing text
"""
import fitz
from doclayout_yolo import YOLOv10

pdf_path = "test_files/2503.20314v2.pdf"

print("Analyzing text blocks near formulas...\n")
print("=" * 80)

# Load YOLO model
model = YOLOv10("weights/doclayout_yolo_docstructbench_imgsz1024.pt")

# Open PDF
doc = fitz.open(pdf_path)

# Check page 4 (where formulas 1 and 2 are)
page_num = 3  # 0-indexed, so page 4
page = doc[page_num]

print(f"\n【Page {page_num + 1}】\n")

# Detect formulas with YOLO
mat = fitz.Matrix(150 / 72, 150 / 72)
pix = page.get_pixmap(matrix=mat)
temp_img = f"_temp_analyze_page_{page_num}.png"
pix.save(temp_img)

results = model.predict(temp_img, imgsz=1024, conf=0.25, device='cuda', verbose=False)

import os
if os.path.exists(temp_img):
    os.remove(temp_img)

# Get formula bboxes
formula_bboxes = []
if len(results) > 0 and hasattr(results[0], 'boxes'):
    for box in results[0].boxes:
        cls_id = int(box.cls[0].cpu().numpy())
        class_name = model.names[cls_id]

        if class_name.lower() in ['isolate_formula', 'formula']:
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

            formula_bboxes.append(pdf_bbox)
            print(f"Formula detected: bbox={pdf_bbox}")

# Extract all text blocks from PDF
text_dict = page.get_textpage().extractDICT()

print(f"\n{'='*80}\n")
print("Text blocks on this page:\n")

for block_idx, block in enumerate(text_dict.get('blocks', [])):
    if block.get('type') != 0:  # Only text blocks
        continue

    block_bbox = block['bbox']

    # Extract text from this block
    block_text = ''
    for line in block.get('lines', []):
        for span in line.get('spans', []):
            block_text += span.get('text', '')

    if not block_text.strip():
        continue

    # Check if this block is near any formula
    block_rect = fitz.Rect(block_bbox)

    near_formula = False
    for formula_idx, formula_bbox in enumerate(formula_bboxes):
        formula_rect = fitz.Rect(formula_bbox)

        # Check if block overlaps or is very close to formula
        if block_rect.intersects(formula_rect):
            near_formula = True
            print(f"Block {block_idx}: [OVERLAPS Formula {formula_idx}]")
            print(f"  bbox: {block_bbox}")
            print(f"  text: {repr(block_text)}")
            print(f"  Formula bbox: {formula_bbox}")

            # Calculate overlap
            intersection = block_rect & formula_rect
            if not intersection.is_empty:
                intersection_area = intersection.width * intersection.height
                block_area = block_rect.width * block_rect.height
                overlap_ratio = intersection_area / block_area if block_area > 0 else 0
                print(f"  Overlap ratio: {overlap_ratio:.2%}")
            print()
            break

    # Look for the missing text
    if 'velocity' in block_text.lower() or 'ground truth' in block_text.lower():
        print(f"Block {block_idx}: [FOUND TARGET TEXT]")
        print(f"  bbox: {block_bbox}")
        print(f"  text: {repr(block_text)}")
        print(f"  Near formula: {near_formula}")

        # Check distance to nearest formula
        for formula_idx, formula_bbox in enumerate(formula_bboxes):
            formula_rect = fitz.Rect(formula_bbox)
            print(f"  Distance to Formula {formula_idx}:")
            print(f"    Formula bbox: {formula_bbox}")
            print(f"    Horizontal distance: {block_rect.x0 - formula_rect.x1:.1f} (left of formula)")
            print(f"    Vertical distance: {min(abs(block_rect.y0 - formula_rect.y1), abs(block_rect.y1 - formula_rect.y0)):.1f}")
        print()

doc.close()

print("=" * 80)
