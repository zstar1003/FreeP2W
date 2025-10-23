"""
Debug inline math conversion - check what's happening
"""
from docx import Document
import zipfile
from lxml import etree

docx_path = "test_files/result_hybrid_with_inline_math.docx"

# Extract and parse the document XML
with zipfile.ZipFile(docx_path, 'r') as zip_file:
    xml_content = zip_file.read('word/document.xml')

# Parse XML
root = etree.fromstring(xml_content)

# Define namespaces
nsmap = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
}

# Find all paragraphs
paragraphs = root.xpath('.//w:p', namespaces=nsmap)

print(f"Total paragraphs: {len(paragraphs)}")
print("=" * 80)

# Check paragraph 23 (0-indexed, so element 23)
if len(paragraphs) > 23:
    para = paragraphs[23]

    # Get all text
    text_nodes = para.xpath('.//w:t', namespaces=nsmap)
    print(f"\nParagraph 23 text nodes ({len(text_nodes)}):")
    for i, t in enumerate(text_nodes):
        print(f"  {i}: {repr(t.text)}")

    # Get all math nodes
    math_nodes = para.xpath('.//m:oMath', namespaces=nsmap)
    print(f"\nParagraph 23 math nodes ({len(math_nodes)}):")
    for i, m in enumerate(math_nodes):
        math_text = ''.join(m.itertext())
        print(f"  {i}: {repr(math_text)}")

    # Show full paragraph structure
    print(f"\nParagraph 23 XML structure:")
    print(etree.tostring(para, encoding='unicode', pretty_print=True)[:1000])
