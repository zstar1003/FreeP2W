"""
Detailed analysis of smallpdf body text alignment
"""

from docx import Document
import re

docx_path = "test_files/2503.20314v2_smallpdf.docx"
doc = Document(docx_path)

print("="*80)
print("SMALLPDF BODY TEXT ALIGNMENT ANALYSIS")
print("="*80)

alignment_count = {
    'None': 0,
    'LEFT': 0,
    'CENTER': 0,
    'RIGHT': 0,
    'JUSTIFY': 0
}

body_paragraphs = []

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if not text or len(text) < 30:  # Only long paragraphs (body text)
        continue

    # Skip titles, sections, figures
    is_title = len(text) < 100 and text.isupper()
    is_section = bool(re.match(r'^[\d\.]+\s+[A-Z]', text))
    is_figure = text.lower().startswith(('figure', 'fig.', 'fig ', 'table'))

    if is_title or is_section or is_figure:
        continue

    # Get alignment
    if para.alignment is None:
        align_str = 'None'
    else:
        align_str = str(para.alignment).split('.')[-1].replace('WD_ALIGN_PARAGRAPH.', '')

    alignment_count[align_str] = alignment_count.get(align_str, 0) + 1

    if len(body_paragraphs) < 20:
        body_paragraphs.append({
            'idx': i,
            'text': text[:70],
            'align': align_str
        })

print("\nALIGNMENT DISTRIBUTION FOR BODY TEXT (>30 chars):")
print("-"*80)
for align, count in sorted(alignment_count.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  {align:>12s}: {count:3d} paragraphs")

print("\nSAMPLE BODY PARAGRAPHS:")
print("-"*80)
for p in body_paragraphs:
    print(f"[{p['idx']:3d}] {p['align']:>12s} | {p['text']}...")

print("\n" + "="*80)
