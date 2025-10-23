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

# Write to file to avoid encoding issues
with open("verify_expressions_result.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("SEARCHING FOR MATH EXPRESSIONS LIKE u(xt, ctxt, t; θ)\n")
    f.write("=" * 80 + "\n")

    # Find all math elements
    paragraphs = root.xpath('.//w:p', namespaces=nsmap)

    found_expressions = []

    for idx, para in enumerate(paragraphs):
        para_text = ''.join(para.itertext())

        # Check if contains function-like patterns with theta
        if re.search(r'[a-z]\([^)]*θ[^)]*\)', para_text, re.IGNORECASE):
            f.write(f"\nParagraph {idx}:\n")
            f.write(f"Text preview: {para_text[:150]}...\n")

            # Find all math elements in this paragraph
            math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
            f.write(f"Math elements: {len(math_elems)}\n")

            # Check each math element
            for i, math_elem in enumerate(math_elems):
                math_text = ''.join(math_elem.itertext())
                f.write(f"\n  Math element {i+1}:\n")
                f.write(f"    Content: {repr(math_text)}\n")

                # Check if it's a complete expression (contains parentheses)
                if '(' in math_text and ')' in math_text:
                    f.write(f"    Type: ✓ COMPLETE EXPRESSION\n")
                    found_expressions.append(math_text)
                elif math_text in ['θ', 'α', 'β', 'γ', '∈', '×', '∼']:
                    f.write(f"    Type: Single symbol\n")
                else:
                    f.write(f"    Type: Other\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write(f"SUMMARY: Found {len(found_expressions)} complete math expressions\n")
    f.write("=" * 80 + "\n")

    for i, expr in enumerate(found_expressions, 1):
        f.write(f"{i}. {repr(expr)}\n")

print("Results written to verify_expressions_result.txt")
