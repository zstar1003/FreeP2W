"""
Visual Content Detector - Use OpenCV to detect image regions

This approach uses computer vision to detect visual content regions:
1. Edge detection to find content boundaries
2. DBSCAN clustering to merge nearby regions
3. Area filtering to identify significant visual regions
"""

import cv2
import numpy as np
import fitz


class VisualContentDetector:
    """Detect visual content regions using computer vision"""

    def __init__(self, min_region_area=10000, merge_gap=30, page_coverage_threshold=0.15):
        """
        Args:
            min_region_area: Minimum area (px²) for a region to be considered
            merge_gap: Maximum distance (px) to merge nearby regions
            page_coverage_threshold: Minimum page coverage ratio to consider as image
        """
        self.min_region_area = min_region_area
        self.merge_gap = merge_gap
        self.page_coverage_threshold = page_coverage_threshold

    def detect_visual_regions(self, page: fitz.Page, dpi=150):
        """
        Detect visual content regions in a PDF page

        Args:
            page: fitz.Page object
            dpi: DPI for rendering

        Returns:
            list of fitz.Rect: Detected visual regions
        """
        print(f"[INFO] Detecting visual regions on page {page.number + 1}...")

        # Step 1: Convert page to OpenCV image
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = self._pixmap_to_cv_image(pix)

        img_height, img_width = img.shape[:2]
        page_area = img_width * img_height

        # Step 2: Detect edges and find contours
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Use adaptive thresholding for better detection
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Step 3: Extract bounding boxes
        bboxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter by minimum area
            if area > self.min_region_area:
                bboxes.append([x, y, x + w, y + h, area])

        print(f"[INFO] Found {len(bboxes)} candidate regions")

        if not bboxes:
            return []

        # Step 4: Cluster nearby boxes using DBSCAN
        clustered_bboxes = self._cluster_boxes(bboxes)

        print(f"[INFO] After clustering: {len(clustered_bboxes)} regions")

        # Step 5: Show all regions and filter by page coverage
        print(f"[INFO] All clustered regions (showing coverage %):")
        visual_regions = []
        for i, bbox in enumerate(clustered_bboxes, 1):
            x0, y0, x1, y1, area = bbox

            # Calculate coverage ratio
            coverage = area / page_area

            print(f"[INFO]   Region {i}: {x1-x0:.0f}x{y1-y0:.0f} px, coverage: {coverage:.1%}")

            # Keep if coverage is significant (lowered threshold to 5%)
            if coverage > 0.05:  # 5% threshold
                visual_regions.append(bbox)

        print(f"[INFO] Final visual regions (coverage > 5%): {len(visual_regions)}")

        # Step 6: Convert to PDF coordinates
        scale_x = page.rect.width / img_width
        scale_y = page.rect.height / img_height

        pdf_regions = []
        for bbox in visual_regions:
            x0, y0, x1, y1, _ = bbox
            pdf_rect = fitz.Rect(
                x0 * scale_x,
                y0 * scale_y,
                x1 * scale_x,
                y1 * scale_y
            )
            pdf_regions.append(pdf_rect)

        return pdf_regions

    def _cluster_boxes(self, bboxes):
        """Cluster nearby boxes using simple distance-based merging"""
        if len(bboxes) == 1:
            return bboxes

        # Use Union-Find to group nearby boxes
        n = len(bboxes)
        parent = list(range(n))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Check distance between every pair
        for i in range(n):
            for j in range(i + 1, n):
                # Calculate distance between centers
                cx1, cy1 = (bboxes[i][0] + bboxes[i][2]) / 2, (bboxes[i][1] + bboxes[i][3]) / 2
                cx2, cy2 = (bboxes[j][0] + bboxes[j][2]) / 2, (bboxes[j][1] + bboxes[j][3]) / 2

                distance = ((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2) ** 0.5

                # Merge if close enough
                if distance <= self.merge_gap:
                    union(i, j)

        # Group by cluster
        clusters = {}
        for idx in range(n):
            root = find(idx)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(bboxes[idx])

        # Merge boxes in same cluster
        merged = []
        for cluster in clusters.values():
            # Compute union bbox
            x0 = min(b[0] for b in cluster)
            y0 = min(b[1] for b in cluster)
            x1 = max(b[2] for b in cluster)
            y1 = max(b[3] for b in cluster)
            area = (x1 - x0) * (y1 - y0)

            merged.append([x0, y0, x1, y1, area])

        return merged

    @staticmethod
    def _pixmap_to_cv_image(pixmap):
        """Convert fitz pixmap to OpenCV image"""
        img_bytes = pixmap.tobytes("png")
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


# Test function
def test_visual_detector():
    """Test the visual content detector"""

    print("\n" + "=" * 80)
    print(" " * 15 + "OPENCV VISUAL CONTENT DETECTION TEST")
    print("=" * 80)
    print()

    pdf_file = 'test_files/2503.20314v2.pdf'
    pdf = fitz.open(pdf_file)

    detector = VisualContentDetector(
        min_region_area=10000,     # 10k px²
        merge_gap=100,              # 100px merge distance (increased to merge image tiles)
        page_coverage_threshold=0.15  # 15% page coverage
    )

    # Test on pages 3 and 5
    test_pages = [2, 4]

    for page_num in test_pages:
        print("-" * 80)
        print(f"PAGE {page_num + 1}")
        print("-" * 80)

        page = pdf[page_num]

        # Detect visual regions
        visual_regions = detector.detect_visual_regions(page, dpi=150)

        print()
        print(f"DETECTED {len(visual_regions)} VISUAL REGIONS:")
        print()

        for i, region in enumerate(visual_regions, 1):
            width = region.x1 - region.x0
            height = region.y1 - region.y0
            area = width * height

            print(f"{i}. Position: ({region.x0:.1f}, {region.y0:.1f}) -> ({region.x1:.1f}, {region.y1:.1f})")
            print(f"   Size: {width:.1f} x {height:.1f} pt")
            print(f"   Area: {area:.0f} pt^2")
            print()

        print()

    pdf.close()

    print("=" * 80)
    print("Detection complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_visual_detector()
