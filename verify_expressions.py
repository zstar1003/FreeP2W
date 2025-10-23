"""
Verify that complete math expressions like u(xt, ctxt, t; θ) are recognized
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

print("=" * 80)
print("SEARCHING FOR MATH EXPRESSIONS LIKE u(xt, ctxt, t; θ)")
print("=" * 80)

# Find all math elements
paragraphs = root.xpath('.//w:p', namespaces=nsmap)

found_expressions = []

for idx, para in enumerate(paragraphs):
    para_text = ''.join(para.itertext())

    # Check if contains function-like patterns
    if re.search(r'[a-z]\([^)]*θ[^)]*\)', para_text, re.IGNORECASE):
        print(f"\nParagraph {idx}:")
        print(f"Text preview: {para_text[:150]}...")

        # Find all math elements in this paragraph
        math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
        print(f"Math elements: {len(math_elems)}")

        # Check each math element
        for i, math_elem in enumerate(math_elems):
            math_text = ''.join(math_elem.itertext())
            print(f"\n  Math element {i+1}:")
            print(f"    Content: {repr(math_text)}")

            # Check if it's a complete expression (contains parentheses)
            if '(' in math_text and ')' in math_text:
                print(f"    Type: COMPLETE EXPRESSION")
                found_expressions.append(math_text)
            elif math_text in ['θ', 'α', 'β', 'γ', '∈', '×', '∼']:
                print(f"    Type: Single symbol")
            else:
                print(f"    Type: Other")

print("\n" + "=" * 80)
print(f"SUMMARY: Found {len(found_expressions)} complete math expressions")
print("=" * 80)

for i, expr in enumerate(found_expressions, 1):
    print(f"{i}. {repr(expr)}")
