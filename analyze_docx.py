"""
Analyze images in DOCX file
"""
from docx import Document
from docx.oxml.ns import qn

def analyze_docx_images(docx_path):
    """Analyze images in a DOCX file"""
    doc = Document(docx_path)

    image_count = 0
    images_by_page = {}

    for i, para in enumerate(doc.paragraphs):
        # Check for images in runs
        for run in para.runs:
            # Check for inline shapes (images)
            if hasattr(run._element, 'drawing_lst'):
                for drawing in run._element.drawing_lst:
                    image_count += 1

    # Check in shapes
    for shape in doc.inline_shapes:
        image_count += 1
        print(f"Image {image_count}: {shape.width} x {shape.height}")

    print(f"\nTotal images in document: {image_count}")
    print(f"Total inline shapes: {len(doc.inline_shapes)}")

    return image_count

if __name__ == "__main__":
    print("Analyzing result_hybrid.docx...")
    analyze_docx_images("test_files/result_hybrid.docx")
