"""
Verify the formatted output matches smallpdf style
"""

from docx import Document
import re

doc = Document('result_smallpdf_style.docx')

print("="*80)
print("FORMATTED OUTPUT VERIFICATION")
print("="*80)

# Check alignment distribution
alignment_stats = {}
body_samples = []
section_samples = []
figure_samples = []

for i, para in enumerate(doc.paragraphs[:60]):
    text = para.text.strip()
    if not text:
        continue

    has_math = 'oMath' in para._element.xml
    if has_math:
        continue

    # Get alignment
    if para.alignment is None:
        align_str = 'LEFT(None)'
    else:
        align_str = str(para.alignment)

    # Get font info
    font_name = 'N/A'
    font_size = 'N/A'
    for run in para.runs:
        if run.font.name:
            font_name = run.font.name
        if run.font.size:
            font_size = f"{run.font.size.pt:.1f}"
        if font_name != 'N/A':
            break

    # Categorize
    is_section = bool(re.match(r'^[\d\.]+\s+[A-Z]', text))
    is_figure = text.lower().startswith(('figure', 'fig.', 'fig ', 'table'))
    is_title = len(text) < 100 and text.isupper() and not is_figure

    info = {
        'idx': i,
        'text': text[:60],
        'font': font_name,
        'size': font_size,
        'align': align_str
    }

    if is_section and len(section_samples) < 5:
        section_samples.append(info)
    elif is_figure and len(figure_samples) < 3:
        figure_samples.append(info)
    elif not is_section and not is_figure and not is_title and len(text) > 30 and len(body_samples) < 10:
        body_samples.append(info)
        alignment_stats[align_str] = alignment_stats.get(align_str, 0) + 1

print("\n1. BODY TEXT ALIGNMENT DISTRIBUTION:")
print("-"*80)
for align, count in sorted(alignment_stats.items(), key=lambda x: -x[1]):
    print(f"  {align}: {count} paragraphs")

print("\n2. SECTION HEADERS (should be LEFT, Bookman Old Style, 10pt):")
print("-"*80)
for s in section_samples:
    print(f"[{s['idx']:3d}] {s['size']:>5s}pt {s['font']:>20s} {s['align']:>20s} | {s['text']}")

print("\n3. FIGURE CAPTIONS (should be CENTER, Bookman Old Style, 10pt):")
print("-"*80)
for f in figure_samples:
    print(f"[{f['idx']:3d}] {f['size']:>5s}pt {f['font']:>20s} {f['align']:>20s} | {f['text']}")

print("\n4. BODY TEXT SAMPLES (should be JUSTIFY, Bookman Old Style, 10pt):")
print("-"*80)
for b in body_samples[:5]:
    print(f"[{b['idx']:3d}] {b['size']:>5s}pt {b['font']:>20s} {b['align']:>20s} | {b['text']}")

print("\n" + "="*80)
print("VERIFICATION SUMMARY:")
print("-"*80)

# Count correct formatting
correct_sections = sum(1 for s in section_samples if 'LEFT' in s['align'] and s['font'] == 'Bookman Old Style')
correct_figures = sum(1 for f in figure_samples if 'CENTER' in f['align'] and f['font'] == 'Bookman Old Style')
correct_body = sum(1 for b in body_samples if 'JUSTIFY' in b['align'] and b['font'] == 'Bookman Old Style')

print(f"Section headers: {correct_sections}/{len(section_samples)} correctly formatted")
print(f"Figure captions: {correct_figures}/{len(figure_samples)} correctly formatted")
print(f"Body text: {correct_body}/{len(body_samples)} correctly formatted")

if correct_sections == len(section_samples) and correct_figures == len(figure_samples) and correct_body >= len(body_samples) * 0.8:
    print("\n✓ Formatting looks good!")
else:
    print("\n⚠ Some formatting issues detected")

print("="*80)
