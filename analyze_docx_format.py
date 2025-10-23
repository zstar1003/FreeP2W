"""
Analyze DOCX font sizes and formatting
"""

from docx import Document
from collections import Counter

docx_path = "result.docx"
doc = Document(docx_path)

# Analyze font sizes
font_sizes = []
paragraph_info = []

for i, para in enumerate(doc.paragraphs):
    para_text = para.text.strip()
    if not para_text:
        continue

    # Get all run font sizes in this paragraph
    para_sizes = []
    for run in para.runs:
        if run.font.size:
            size_pt = run.font.size.pt
            para_sizes.append(size_pt)
            font_sizes.append(size_pt)

    # Get alignment
    alignment = para.alignment

    # Store info
    if para_sizes:
        most_common_size = Counter(para_sizes).most_common(1)[0][0]
        paragraph_info.append({
            'index': i,
            'text': para_text[:60] + '...' if len(para_text) > 60 else para_text,
            'size': most_common_size,
            'alignment': alignment,
            'runs': len(para.runs)
        })

# Count font sizes
size_counter = Counter(font_sizes)

print("=" * 80)
print("FONT SIZE ANALYSIS")
print("=" * 80)
print("\nFont size distribution:")
for size, count in sorted(size_counter.items()):
    print(f"  {size}pt: {count} runs ({count/len(font_sizes)*100:.1f}%)")

most_common_size = size_counter.most_common(1)[0][0]
print(f"\nMost common font size: {most_common_size}pt")

# Detect table of contents section
print("\n" + "=" * 80)
print("PARAGRAPH ANALYSIS (First 30 paragraphs)")
print("=" * 80)

for info in paragraph_info[:30]:
    alignment_str = str(info['alignment']).split('.')[-1] if info['alignment'] else 'None'
    print(f"[{info['index']:3d}] Size={info['size']:4.1f}pt Align={alignment_str:10s} | {info['text']}")

# Try to detect TOC
print("\n" + "=" * 80)
print("TABLE OF CONTENTS DETECTION")
print("=" * 80)

toc_candidates = []
for info in paragraph_info[:50]:
    text = info['text']
    # Common TOC patterns
    if any(pattern in text.lower() for pattern in ['abstract', 'introduction', 'conclusion', 'references', 'appendix']):
        # Check if it looks like a TOC entry (short, possibly with dots or page numbers)
        if len(text) < 100:
            toc_candidates.append(info)

print(f"\nFound {len(toc_candidates)} potential TOC entries:")
for info in toc_candidates[:15]:
    print(f"  [{info['index']:3d}] {info['text']}")
