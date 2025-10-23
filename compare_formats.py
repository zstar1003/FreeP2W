"""
Compare our formatted file with smallpdf
"""

from docx import Document
import re

def analyze_doc(path, name):
    doc = Document(path)

    print(f"\n{'='*80}")
    print(f"{name}")
    print(f"{'='*80}")

    # Sample paragraphs
    samples = {
        'body': [],
        'sections': [],
        'figures': []
    }

    for i, para in enumerate(doc.paragraphs[:60]):
        text = para.text.strip()
        if not text:
            continue

        has_math = 'oMath' in para._element.xml
        if has_math:
            continue

        # Get paragraph info
        alignment = str(para.alignment).split('.')[-1] if para.alignment else 'None'
        font_name = 'N/A'
        font_size = 'N/A'

        if para.runs:
            for run in para.runs:
                if run.font.name:
                    font_name = run.font.name
                if run.font.size:
                    font_size = f"{run.font.size.pt:.1f}"
                if font_name != 'N/A' and font_size != 'N/A':
                    break

        # Categorize
        is_section = bool(re.match(r'^[\d\.]+\s+[A-Z]', text))
        is_figure = text.lower().startswith(('figure', 'fig.', 'fig ', 'table'))

        info = {
            'idx': i,
            'text': text[:55],
            'font': font_name,
            'size': font_size,
            'align': alignment
        }

        if is_section and len(samples['sections']) < 5:
            samples['sections'].append(info)
        elif is_figure and len(samples['figures']) < 3:
            samples['figures'].append(info)
        elif not is_section and not is_figure and len(samples['body']) < 5:
            samples['body'].append(info)

    # Print results
    print("\nSECTION HEADERS:")
    print("-"*80)
    for s in samples['sections']:
        print(f"[{s['idx']:3d}] {s['size']:>5s}pt {s['font']:>20s} {s['align']:>12s} | {s['text']}")

    print("\nFIGURE CAPTIONS:")
    print("-"*80)
    for f in samples['figures']:
        print(f"[{f['idx']:3d}] {f['size']:>5s}pt {f['font']:>20s} {f['align']:>12s} | {f['text']}")

    print("\nBODY TEXT:")
    print("-"*80)
    for b in samples['body']:
        print(f"[{b['idx']:3d}] {b['size']:>5s}pt {b['font']:>20s} {b['align']:>12s} | {b['text']}")

# Compare
print("="*80)
print("FORMAT COMPARISON: OUR OUTPUT vs SMALLPDF")
print("="*80)

analyze_doc("test_files/2503.20314v2_smallpdf.docx", "SMALLPDF (REFERENCE)")
analyze_doc("result_smallpdf_style.docx", "OUR OUTPUT (FORMATTED)")
