"""
Find and display table of contents section
"""

from docx import Document

docx_path = "result.docx"
doc = Document(docx_path)

print("=" * 80)
print("DOCUMENT BEGINNING (First 50 paragraphs)")
print("=" * 80)

for i, para in enumerate(doc.paragraphs[:50]):
    text = para.text.strip()
    if text:
        alignment = str(para.alignment).split('.')[-1] if para.alignment else 'None'

        # Check for math elements
        has_math = 'oMath' in para._element.xml if hasattr(para, '_element') else False
        math_str = ' [MATH]' if has_math else ''

        # Get font size
        size = 'N/A'
        if para.runs:
            for run in para.runs:
                if run.font.size:
                    size = f"{run.font.size.pt:.1f}"
                    break

        print(f"[{i:3d}] {size:>5s}pt {alignment:>10s}{math_str} | {text[:70]}")
