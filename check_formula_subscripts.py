"""
Check for x0, x1, xt, vt subscripts specifically
"""
import zipfile
from lxml import etree

docx_path = "test_files/result_hybrid_with_inline_math.docx"

with zipfile.ZipFile(docx_path, 'r') as zip_file:
    xml_content = zip_file.read('word/document.xml')

root = etree.fromstring(xml_content)

nsmap = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
}

# Write to file
with open("formula_subscripts.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("FORMULA VARIABLE SUBSCRIPTS (x0, x1, xt, vt, etc.)\n")
    f.write("=" * 80 + "\n")

    # Find paragraphs containing formula-related keywords
    paragraphs = root.xpath('.//w:p', namespaces=nsmap)

    target_vars = ['x0', 'x1', 'xt', 'vt']

    for para in paragraphs:
        para_text = ''.join(para.itertext())

        # Check if contains target variables
        has_target = any(var in para_text for var in target_vars)

        if has_target:
            f.write(f"\n{'='*80}\n")
            f.write(f"Paragraph: {para_text[:150]}...\n")
            f.write(f"\n")

            # Find all subscripts in this paragraph
            subscripts = para.xpath('.//m:sSub', namespaces=nsmap)

            if len(subscripts) > 0:
                f.write(f"Subscripts found: {len(subscripts)}\n")
                for sub in subscripts:
                    base_elem = sub.find('.//m:e//m:t', namespaces=nsmap)
                    sub_elem = sub.find('.//m:sub//m:t', namespaces=nsmap)

                    if base_elem is not None and sub_elem is not None:
                        base = base_elem.text or ""
                        subscript = sub_elem.text or ""
                        f.write(f"  - {base}_{subscript}\n")
            else:
                f.write(f"NO subscripts found (might be in expression or plain text)\n")

            # Also check for oMath elements
            math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
            f.write(f"Total math elements: {len(math_elems)}\n")

print("Results written to formula_subscripts.txt")
