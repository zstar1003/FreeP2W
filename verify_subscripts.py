"""
Verify subscript recognition and OMML generation
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
with open("subscript_verification.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("SUBSCRIPT RECOGNITION VERIFICATION\n")
    f.write("=" * 80 + "\n")

    # Find all m:sSub elements (subscript structures)
    subscripts = root.xpath('.//m:sSub', namespaces=nsmap)

    f.write(f"\nTotal subscript elements found: {len(subscripts)}\n\n")

    # Show first 10 subscripts
    for i, sub_elem in enumerate(subscripts[:15]):
        # Get base and subscript content
        base_elem = sub_elem.find('.//m:e//m:t', namespaces=nsmap)
        sub_content_elem = sub_elem.find('.//m:sub//m:t', namespaces=nsmap)

        if base_elem is not None and sub_content_elem is not None:
            base = base_elem.text or ""
            subscript = sub_content_elem.text or ""

            f.write(f"{i+1}. {base}_{subscript}\n")

            # Find the parent paragraph to get context
            para = sub_elem
            while para is not None and para.tag != '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p':
                para = para.getparent()

            if para is not None:
                para_text = ''.join(para.itertext())
                f.write(f"   Context: {para_text[:100]}...\n")
        else:
            f.write(f"{i+1}. [Parsing error]\n")

        f.write("\n")

    f.write("=" * 80 + "\n")
    f.write("SAMPLE SUBSCRIPT XML STRUCTURE\n")
    f.write("=" * 80 + "\n")

    if len(subscripts) > 0:
        sample = subscripts[0]
        xml_str = etree.tostring(sample, encoding='unicode', pretty_print=True)
        f.write(xml_str[:500])
        f.write("\n...")

print("Verification written to subscript_verification.txt")
