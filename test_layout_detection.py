"""
Test Surya Layout Detection - Only detect image regions

This script tests Surya's ability to detect Picture/Figure regions in PDF
"""

import fitz
from PIL import Image
import io
from surya.foundation import FoundationPredictor
from surya.layout import LayoutPredictor


def test_layout_detection():
    """Test layout detection and show image regions"""

    print("\n" + "=" * 80)
    print(" " * 20 + "SURYA LAYOUT DETECTION - IMAGE REGIONS")
    print("=" * 80)
    print()

    pdf_file = 'test_files/2503.20314v2.pdf'

    # Load Surya model
    print("Loading Surya layout detection model...")
    foundation_predictor = FoundationPredictor(device='cpu')
    layout_predictor = LayoutPredictor(foundation_predictor)
    print("Model loaded!")
    print()

    # Open PDF
    pdf = fitz.open(pdf_file)

    # Test on specific pages
    test_pages = [2, 4]  # Pages 3 and 5 (0-indexed)

    for page_num in test_pages:
        print("-" * 80)
        print(f"PAGE {page_num + 1} - Layout Detection Results")
        print("-" * 80)

        page = pdf[page_num]
        page_width = page.rect.width
        page_height = page.rect.height

        print(f"Page size: {page_width:.1f} x {page_height:.1f} pt")
        print()

        # Convert to image for detection
        mat = fitz.Matrix(2, 2)  # 2x zoom for better detection
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        print(f"Image size: {img.width} x {img.height} px")
        print()

        # Detect layout
        print("Running layout detection...")
        results = layout_predictor([img])

        # Count by type
        region_counts = {}
        for detection in results[0].bboxes:
            label = detection.label
            region_counts[label] = region_counts.get(label, 0) + 1

        print(f"\nDetected {len(results[0].bboxes)} total regions:")
        for label, count in sorted(region_counts.items()):
            print(f"  {label:20s}: {count:3d}")

        print()
        print("=" * 80)
        print("IMAGE/FIGURE REGIONS DETAILS:")
        print("=" * 80)

        # Show only Picture/Figure regions
        image_regions = []
        for detection in results[0].bboxes:
            if detection.label in ['Picture', 'Figure']:
                # Convert from image pixels to PDF points
                x0, y0, x1, y1 = detection.bbox

                scale_x = page_width / img.width
                scale_y = page_height / img.height

                pdf_bbox = [
                    x0 * scale_x,
                    y0 * scale_y,
                    x1 * scale_x,
                    y1 * scale_y
                ]

                width = pdf_bbox[2] - pdf_bbox[0]
                height = pdf_bbox[3] - pdf_bbox[1]

                image_regions.append({
                    'type': detection.label,
                    'bbox': pdf_bbox,
                    'width': width,
                    'height': height
                })

        if image_regions:
            print(f"\nFound {len(image_regions)} image regions:")
            print()
            for i, region in enumerate(image_regions, 1):
                bbox = region['bbox']
                print(f"{i}. {region['type']}")
                print(f"   Position: ({bbox[0]:.1f}, {bbox[1]:.1f}) -> ({bbox[2]:.1f}, {bbox[3]:.1f})")
                print(f"   Size: {region['width']:.1f} x {region['height']:.1f} pt")
                print(f"   Area: {region['width'] * region['height']:.0f} pt²")
                print()
        else:
            print("\nNo image regions detected!")
            print()

        print()

    pdf.close()

    print("=" * 80)
    print("Detection complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_layout_detection()
