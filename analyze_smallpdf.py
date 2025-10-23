"""
Analyze smallpdf.docx to understand its formatting
"""

from docx import Document
from docx.shared import Pt
from collections import Counter
import re

docx_path = "test_files/2503.20314v2_smallpdf.docx"
doc = Document(docx_path)

print("=" * 80)
print("SMALLPDF.DOCX FORMAT ANALYSIS")
print("=" * 80)

# Analyze font sizes
font_sizes = []
font_names = []
paragraph_info = []

for i, para in enumerate(doc.paragraphs[:100]):
    text = para.text.strip()
    if not text:
        continue

    # Get paragraph format
    para_sizes = []
    para_fonts = []

    for run in para.runs:
        if run.font.size:
            para_sizes.append(run.font.size.pt)
            font_sizes.append(run.font.size.pt)
        if run.font.name:
            para_fonts.append(run.font.name)
            font_names.append(run.font.name)

    # Get alignment
    alignment = para.alignment

    # Get spacing
    space_before = para.paragraph_format.space_before
    space_after = para.paragraph_format.space_after
    line_spacing = para.paragraph_format.line_spacing

    if para_sizes:
        most_common_size = Counter(para_sizes).most_common(1)[0][0]
        most_common_font = Counter(para_fonts).most_common(1)[0][0] if para_fonts else 'N/A'

        paragraph_info.append({
            'index': i,
            'text': text[:70],
            'size': most_common_size,
            'font': most_common_font,
            'alignment': alignment,
            'space_before': space_before,
            'space_after': space_after,
            'line_spacing': line_spacing,
        })

# Font size distribution
print("\n1. FONT SIZE DISTRIBUTION:")
print("-" * 80)
size_counter = Counter(font_sizes)
for size, count in sorted(size_counter.items()):
    print(f"  {size:5.1f}pt: {count:4d} runs ({count/len(font_sizes)*100:5.1f}%)")

most_common_size = size_counter.most_common(1)[0][0]
print(f"\n  Most common: {most_common_size}pt")

# Font name distribution
print("\n2. FONT NAME DISTRIBUTION:")
print("-" * 80)
font_counter = Counter(font_names)
for font, count in font_counter.most_common(5):
    print(f"  {font}: {count} runs ({count/len(font_names)*100:.1f}%)")

# Paragraph details
print("\n3. PARAGRAPH DETAILS (First 50):")
print("-" * 80)

# Don't print here, save directly to file
# This avoids UnicodeEncodeError

# Check section headers
print("\n4. SECTION HEADERS ANALYSIS:")
print("-" * 80)

# Don't print here either

# Check figure captions
print("\n5. FIGURE CAPTIONS ANALYSIS:")
print("-" * 80)

# Don't print here either

print("\nSaving detailed analysis to file...")

# Save to file
with open('smallpdf_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("SMALLPDF.DOCX FORMAT ANALYSIS\n")
    f.write("=" * 80 + "\n")

    f.write("\n1. FONT SIZE DISTRIBUTION:\n")
    f.write("-" * 80 + "\n")
    for size, count in sorted(size_counter.items()):
        f.write(f"  {size:5.1f}pt: {count:4d} runs ({count/len(font_sizes)*100:5.1f}%)\n")
    f.write(f"\n  Most common: {most_common_size}pt\n")

    f.write("\n2. FONT NAME DISTRIBUTION:\n")
    f.write("-" * 80 + "\n")
    for font, count in font_counter.most_common(5):
        f.write(f"  {font}: {count} runs ({count/len(font_names)*100:.1f}%)\n")

    f.write("\n3. PARAGRAPH DETAILS (First 50):\n")
    f.write("-" * 80 + "\n")
    for info in paragraph_info[:50]:
        alignment_str = str(info['alignment']).split('.')[-1].replace('WD_ALIGN_PARAGRAPH.', '') if info['alignment'] else 'None'
        space_before_str = f"{info['space_before'].pt:.1f}" if info['space_before'] else 'N/A'
        space_after_str = f"{info['space_after'].pt:.1f}" if info['space_after'] else 'N/A'
        line_spacing_str = f"{info['line_spacing']:.2f}" if info['line_spacing'] else 'N/A'
        f.write(f"[{info['index']:4d}] {info['size']:5.1f}pt {info['font']:>20s} {alignment_str:>12s} "
                f"{space_before_str:>6s} {space_after_str:>6s} {line_spacing_str:>10s} | {info['text'][:50]}\n")

    f.write("\n4. SECTION HEADERS ANALYSIS:\n")
    f.write("-" * 80 + "\n")
    for info in paragraph_info[:50]:
        text = info['text']
        if re.match(r'^[\d\.]+\s+[A-Z]', text) or (len(text) < 50 and text.isupper()):
            alignment_str = str(info['alignment']).split('.')[-1].replace('WD_ALIGN_PARAGRAPH.', '') if info['alignment'] else 'None'
            f.write(f"[{info['index']:3d}] {info['size']:5.1f}pt {info['font']:>20s} {alignment_str:>12s} | {text[:60]}\n")

    f.write("\n5. FIGURE CAPTIONS ANALYSIS:\n")
    f.write("-" * 80 + "\n")
    for info in paragraph_info[:50]:
        text = info['text']
        if text.lower().startswith(('figure', 'fig.', 'fig ', 'table')):
            alignment_str = str(info['alignment']).split('.')[-1].replace('WD_ALIGN_PARAGRAPH.', '') if info['alignment'] else 'None'
            f.write(f"[{info['index']:3d}] {info['size']:5.1f}pt {info['font']:>20s} {alignment_str:>12s} | {text[:60]}\n")

print("\nAnalysis saved to: smallpdf_analysis.txt")
