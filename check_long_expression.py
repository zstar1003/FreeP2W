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

for para in paragraphs:
    para_text = ''.join(para.itertext())

    if 'L=Ex0' in para_text:
        print(f"Found paragraph: {para_text[:100]}...")

        # Find the math element
        math_elems = para.xpath('.//m:oMath', namespaces=nsmap)

        if len(math_elems) > 0:
            math_elem = math_elems[0]

            # Get all subscripts and their positions
            subscripts = math_elem.xpath('.//m:sSub', namespaces=nsmap)

            print(f"\nTotal subscripts: {len(subscripts)}\n")

            for i, sub in enumerate(subscripts):
                base = sub.find('.//m:e//m:t', namespaces=nsmap)
                sub_elem = sub.find('.//m:sub//m:t', namespaces=nsmap)

                if base is not None and sub_elem is not None:
                    print(f"{i+1}. {base.text}_{sub_elem.text}")

            # Check the full text
            full_text = ''.join(math_elem.itertext())
            print(f"\nFull expression text:\n{full_text}")

            # Count how many times 'ctxt' appears
            print(f"\nOccurrences of 'ctxt': {full_text.count('ctxt')}")
            print(f"Occurrences of 'c_t': should be 0 (should be c_txt)")

        break
