"""
Verify enhanced expression recognition including x0 ∼N(0, I)
"""
import zipfile
from lxml import etree
import re

docx_path = "test_files/result_hybrid_with_inline_math.docx"

with zipfile.ZipFile(docx_path, 'r') as zip_file:
    xml_content = zip_file.read('word/document.xml')

root = etree.fromstring(xml_content)

nsmap = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
}

# Write to file
with open("enhanced_expressions_result.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("ENHANCED MATH EXPRESSION RECOGNITION\n")
    f.write("=" * 80 + "\n")

    # Find all math elements
    paragraphs = root.xpath('.//w:p', namespaces=nsmap)

    all_expressions = []

    for idx, para in enumerate(paragraphs):
        para_text = ''.join(para.itertext())

        # Find all math elements in this paragraph
        math_elems = para.xpath('.//m:oMath', namespaces=nsmap)

        if len(math_elems) > 0:
            # Check for interesting patterns
            has_distribution = '∼' in para_text or '~' in para_text
            has_set_relation = '∈' in para_text
            has_equation = '=' in para_text

            if has_distribution or has_set_relation or has_equation:
                f.write(f"\n{'='*80}\n")
                f.write(f"Paragraph {idx}:\n")
                f.write(f"Text: {para_text[:200]}...\n")
                f.write(f"Math elements: {len(math_elems)}\n")

                for i, math_elem in enumerate(math_elems):
                    math_text = ''.join(math_elem.itertext())
                    f.write(f"\n  Math {i+1}: {repr(math_text)}\n")

                    # Classify the expression
                    if '∼' in math_text:
                        f.write(f"    Type: DISTRIBUTION (e.g., x0 ∼N(0, I))\n")
                        all_expressions.append(('distribution', math_text))
                    elif '∈' in math_text and '(' not in math_text:
                        f.write(f"    Type: SET RELATION (e.g., x ∈ R)\n")
                        all_expressions.append(('set_relation', math_text))
                    elif '=' in math_text:
                        f.write(f"    Type: EQUATION\n")
                        all_expressions.append(('equation', math_text))
                    elif '(' in math_text and ')' in math_text:
                        f.write(f"    Type: FUNCTION CALL\n")
                        all_expressions.append(('function', math_text))
                    else:
                        f.write(f"    Type: OTHER\n")
                        all_expressions.append(('other', math_text))

    f.write("\n" + "=" * 80 + "\n")
    f.write("SUMMARY BY TYPE\n")
    f.write("=" * 80 + "\n")

    # Group by type
    from collections import defaultdict
    by_type = defaultdict(list)
    for typ, expr in all_expressions:
        by_type[typ].append(expr)

    for typ, exprs in by_type.items():
        f.write(f"\n{typ.upper()}: {len(exprs)} expressions\n")
        for expr in exprs[:5]:  # Show first 5
            f.write(f"  - {repr(expr)}\n")

print("Results written to enhanced_expressions_result.txt")
