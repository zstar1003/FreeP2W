"""
Verify that minimal formatting preserved original formatting
Compare result.docx with result_minimal_format.docx
"""

from docx import Document
from collections import Counter

def analyze_doc(path):
    """Analyze document formatting"""
    doc = Document(path)

    info = {
        'font_names': [],
        'font_sizes': [],
        'alignments': [],
        'none_font_count': 0,
        'set_font_count': 0
    }

    for para in doc.paragraphs:
        if para.alignment is not None:
            info['alignments'].append(para.alignment)

        for run in para.runs:
            # Check font name
            if run.font.name is None:
                info['none_font_count'] += 1
            else:
                info['set_font_count'] += 1
                info['font_names'].append(run.font.name)

            # Check font size
            if run.font.size:
                info['font_sizes'].append(run.font.size.pt)

    return info

print("=" * 80)
print("VERIFYING MINIMAL FORMAT PRESERVATION")
print("=" * 80)

print("\n1. ORIGINAL result.docx:")
print("-" * 80)
original = analyze_doc('result.docx')
print(f"  Font names set: {original['set_font_count']}")
print(f"  Font names None: {original['none_font_count']}")
if original['font_names']:
    print(f"  Set fonts: {Counter(original['font_names']).most_common()}")
if original['font_sizes']:
    print(f"  Font sizes: {Counter(original['font_sizes']).most_common()}")

print("\n2. FORMATTED result_minimal_format.docx:")
print("-" * 80)
formatted = analyze_doc('result_minimal_format.docx')
print(f"  Font names set: {formatted['set_font_count']}")
print(f"  Font names None: {formatted['none_font_count']}")
if formatted['font_names']:
    print(f"  Set fonts: {Counter(formatted['font_names']).most_common()}")
if formatted['font_sizes']:
    print(f"  Font sizes: {Counter(formatted['font_sizes']).most_common()}")

print("\n3. COMPARISON:")
print("-" * 80)

# Check if None fonts stayed None
if formatted['none_font_count'] < original['none_font_count']:
    print("  ❌ WARNING: Some None fonts were changed to explicit fonts!")
    print(f"     Original None count: {original['none_font_count']}")
    print(f"     Formatted None count: {formatted['none_font_count']}")
    print(f"     Difference: {original['none_font_count'] - formatted['none_font_count']}")
else:
    print("  ✅ Good: None fonts were preserved")

# Check if math fonts were preserved
original_fonts = set(original['font_names'])
formatted_fonts = set(formatted['font_names'])

if 'CMR10' in original_fonts or 'CMMI10' in original_fonts:
    math_fonts = {'CMR10', 'CMMI10'} & original_fonts
    if math_fonts <= formatted_fonts:
        print(f"  ✅ Good: Math fonts preserved: {math_fonts}")
    else:
        print(f"  ❌ WARNING: Math fonts lost: {math_fonts - formatted_fonts}")

# Check font size unification
original_sizes = Counter(original['font_sizes'])
formatted_sizes = Counter(formatted['font_sizes'])

print(f"\n  Original size distribution: {dict(original_sizes)}")
print(f"  Formatted size distribution: {dict(formatted_sizes)}")

# Check if body text sizes (9-11pt) were unified to 10pt
body_sizes_original = [s for s in original['font_sizes'] if 9 <= s <= 11]
body_sizes_formatted = [s for s in formatted['font_sizes'] if 9 <= s <= 11]

if body_sizes_original:
    original_varied = len(set(body_sizes_original)) > 1
    formatted_unified = len(set(body_sizes_formatted)) == 1 and body_sizes_formatted[0] == 10.0

    if original_varied and formatted_unified:
        print(f"  ✅ Good: Body text sizes (9-11pt) unified to 10pt")
    elif not original_varied:
        print(f"  ℹ️  Body text sizes were already unified")

print("\n" + "=" * 80)
