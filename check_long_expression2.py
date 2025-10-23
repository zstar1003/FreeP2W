"""
Check the long expression in detail
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

# Find the long expression
paragraphs = root.xpath('.//w:p', namespaces=nsmap)

with open("long_expression_check.txt", "w", encoding="utf-8") as f:
    for para in paragraphs:
        para_text = ''.join(para.itertext())

        if 'L=Ex0' in para_text:
            f.write(f"Found paragraph: {para_text[:100]}...\n")

            # Find the math element
            math_elems = para.xpath('.//m:oMath', namespaces=nsmap)

            if len(math_elems) > 0:
                math_elem = math_elems[0]

                # Get all subscripts and their positions
                subscripts = math_elem.xpath('.//m:sSub', namespaces=nsmap)

                f.write(f"\nTotal subscripts: {len(subscripts)}\n\n")

                for i, sub in enumerate(subscripts):
                    base = sub.find('.//m:e//m:t', namespaces=nsmap)
                    sub_elem = sub.find('.//m:sub//m:t', namespaces=nsmap)

                    if base is not None and sub_elem is not None:
                        f.write(f"{i+1}. {base.text}_{sub_elem.text}\n")

                # Check the full text
                full_text = ''.join(math_elem.itertext())
                f.write(f"\nFull expression text:\n{full_text}\n")

                # Count how many times 'ctxt' appears
                f.write(f"\nOccurrences of 'ctxt': {full_text.count('ctxt')}\n")
                f.write(f"Occurrences of 'xt': {full_text.count('xt')}\n")

            break

print("Results written to long_expression_check.txt")
