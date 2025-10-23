"""
Verify subscripts within expressions like u(xt,ctxt,t;θ) and x0 ∼N(0,I)
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
with open("expression_internal_subscripts.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("SUBSCRIPTS WITHIN EXPRESSIONS VERIFICATION\n")
    f.write("=" * 80 + "\n")

    # Find paragraphs containing target expressions
    paragraphs = root.xpath('.//w:p', namespaces=nsmap)

    # Target 1: u(xt,ctxt,t;θ)
    f.write("\n" + "=" * 80 + "\n")
    f.write("TARGET 1: u(xt,ctxt,t;θ)\n")
    f.write("=" * 80 + "\n")

    for para in paragraphs:
        para_text = ''.join(para.itertext())

        if 'u(xt' in para_text or 'u(xt' in para_text.replace(' ', ''):
            f.write(f"\nParagraph: {para_text[:150]}...\n")

            # Find all math elements
            math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
            f.write(f"Math elements: {len(math_elems)}\n\n")

            for i, math_elem in enumerate(math_elems):
                math_text = ''.join(math_elem.itertext())
                if 'u(' in math_text or 'xt' in math_text:
                    f.write(f"Math element {i+1}:\n")
                    f.write(f"  Text: {math_text}\n")

                    # Count subscripts within this math element
                    subscripts = math_elem.xpath('.//m:sSub', namespaces=nsmap)
                    f.write(f"  Subscripts inside: {len(subscripts)}\n")

                    if len(subscripts) > 0:
                        for j, sub in enumerate(subscripts):
                            base = sub.find('.//m:e//m:t', namespaces=nsmap)
                            sub_elem = sub.find('.//m:sub//m:t', namespaces=nsmap)
                            if base is not None and sub_elem is not None:
                                f.write(f"    {j+1}. {base.text}_{sub_elem.text}\n")

                    # Show XML structure
                    xml_str = etree.tostring(math_elem, encoding='unicode', pretty_print=False)
                    f.write(f"  XML (first 300 chars): {xml_str[:300]}...\n")
                    f.write("\n")

    # Target 2: x0 ∼N(0,I)
    f.write("\n" + "=" * 80 + "\n")
    f.write("TARGET 2: x0 ∼N(0,I)\n")
    f.write("=" * 80 + "\n")

    for para in paragraphs:
        para_text = ''.join(para.itertext())

        if ('x0' in para_text or 'x0' in para_text.replace(' ', '')) and '∼N' in para_text:
            f.write(f"\nParagraph: {para_text[:150]}...\n")

            # Find all math elements
            math_elems = para.xpath('.//m:oMath', namespaces=nsmap)
            f.write(f"Math elements: {len(math_elems)}\n\n")

            for i, math_elem in enumerate(math_elems):
                math_text = ''.join(math_elem.itertext())
                if 'x0' in math_text or '∼N' in math_text:
                    f.write(f"Math element {i+1}:\n")
                    f.write(f"  Text: {math_text}\n")

                    # Count subscripts within this math element
                    subscripts = math_elem.xpath('.//m:sSub', namespaces=nsmap)
                    f.write(f"  Subscripts inside: {len(subscripts)}\n")

                    if len(subscripts) > 0:
                        for j, sub in enumerate(subscripts):
                            base = sub.find('.//m:e//m:t', namespaces=nsmap)
                            sub_elem = sub.find('.//m:sub//m:t', namespaces=nsmap)
                            if base is not None and sub_elem is not None:
                                f.write(f"    {j+1}. {base.text}_{sub_elem.text}\n")

print("Verification written to expression_internal_subscripts.txt")
