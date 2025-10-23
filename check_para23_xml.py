"""
Check the actual XML content for paragraph 23
"""
import zipfile
from lxml import etree

# Check processed file
docx_path = "test_files/result_hybrid_with_inline_math.docx"

with zipfile.ZipFile(docx_path, 'r') as zip_file:
    xml_content = zip_file.read('word/document.xml')

root = etree.fromstring(xml_content)

nsmap = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
}

# Find paragraph with "latent space"
paragraphs = root.xpath('.//w:p', namespaces=nsmap)

for idx, para in enumerate(paragraphs):
    para_text = ''.join(para.itertext())
    if 'latent space' in para_text.lower():
        print(f"Found paragraph {idx} with 'latent space'")
        print(f"Full text: {para_text[:200]}")
        print("\n" + "=" * 80)
        print("XML structure:")
        print("=" * 80)

        # Pretty print with encoding handling
        xml_str = etree.tostring(para, encoding='unicode', pretty_print=True)
        # Print first 2000 chars
        print(xml_str[:2000])

        print("\n" + "=" * 80)
        print("Math elements:")
        math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
        for i, m in enumerate(math_elems):
            print(f"\nMath {i}:")
            math_xml = etree.tostring(m, encoding='unicode', pretty_print=False)
            print(f"  XML: {math_xml[:200]}")
            print(f"  Text: {repr(''.join(m.itertext()))}")

        break
