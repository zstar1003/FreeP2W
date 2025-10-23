"""
Detailed paragraph-by-paragraph comparison of a specific section
to understand structural differences
"""

from docx import Document

def get_detailed_section(path, start_text, num_paras=15):
    """Get detailed paragraph info starting from a specific text"""
    doc = Document(path)
    capturing = False
    results = []

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        if not capturing and start_text.lower() in text.lower():
            capturing = True

        if capturing:
            # Get paragraph details
            info = {
                'index': i,
                'text': text[:200] if text else '[EMPTY]',
                'alignment': str(para.alignment) if para.alignment is not None else 'None',
                'run_count': len(para.runs),
                'has_math': 'oMath' in para._element.xml if hasattr(para, '_element') else False
            }

            # Get font info from first run
            if para.runs:
                first_run = para.runs[0]
                info['font_name'] = first_run.font.name if first_run.font.name else 'None'
                info['font_size'] = f"{first_run.font.size.pt}pt" if first_run.font.size else 'None'
            else:
                info['font_name'] = 'N/A'
                info['font_size'] = 'N/A'

            results.append(info)

            if len(results) >= num_paras:
                break

    return results

# Find a common section to compare
start_text = "In this section, we will provide a detailed introduction"

print("=" * 80)
print("DETAILED SECTION COMPARISON")
print("=" * 80)
print(f"\nStarting from: '{start_text}'")
print("\n")

print("SMALLPDF:")
print("-" * 80)
smallpdf_section = get_detailed_section('test_files/2503.20314v2_smallpdf.docx', start_text, 15)
for info in smallpdf_section:
    print(f"\nPara {info['index']}: (runs: {info['run_count']}, align: {info['alignment']}, font: {info['font_name']} {info['font_size']}, math: {info['has_math']})")
    print(f"  Text: {info['text']}")

print("\n" + "=" * 80)
print("OUR RESULT:")
print("-" * 80)
our_section = get_detailed_section('result.docx', start_text, 15)
for info in our_section:
    print(f"\nPara {info['index']}: (runs: {info['run_count']}, align: {info['alignment']}, font: {info['font_name']} {info['font_size']}, math: {info['has_math']})")
    print(f"  Text: {info['text']}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

print(f"\nSmallpdf paragraph count in section: {len(smallpdf_section)}")
print(f"Our paragraph count in section: {len(our_section)}")
print(f"Difference: {len(smallpdf_section) - len(our_section)}")

# Check if we're merging paragraphs
smallpdf_total_text = ' '.join([p['text'] for p in smallpdf_section])
our_total_text = ' '.join([p['text'] for p in our_section])

print(f"\nSmallpdf total chars: {len(smallpdf_total_text)}")
print(f"Our total chars: {len(our_total_text)}")

if len(smallpdf_section) > len(our_section):
    print(f"\nSmallpdf has {len(smallpdf_section) - len(our_section)} MORE paragraphs in this section")
    print("This suggests we are MERGING content into fewer paragraphs")
elif len(our_section) > len(smallpdf_section):
    print(f"\nWe have {len(our_section) - len(smallpdf_section)} MORE paragraphs in this section")
    print("This suggests we are SPLITTING content into more paragraphs")
else:
    print("\nSame paragraph count - differences are in formatting/structure")

print("=" * 80)
