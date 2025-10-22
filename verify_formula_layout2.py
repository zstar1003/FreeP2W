"""
Verify formula layout - check actual XML structure
"""
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

docx_path = "test_files/result_hybrid.docx"

doc = Document(docx_path)

print("Checking formula paragraph structure...\n")
print("=" * 80)

for idx, para in enumerate(doc.paragraphs):
    # Look for paragraphs with math zones (formulas)
    para_xml_bytes = para._element.xml
    para_xml_str = para_xml_bytes.decode('utf-8') if isinstance(para_xml_bytes, bytes) else str(para_xml_bytes)

    if 'm:oMath' in para_xml_str and '(' in para.text:
        print(f"\nParagraph {idx}:")
        print(f"  Text preview: {para.text[:80]}")

        # Parse the XML to check element order
        nsmap = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }

        # Get all w:r (run) elements in order
        runs_xml = para._element.findall(qn('w:r'))
        print(f"  Number of w:r elements: {len(runs_xml)}")

        for run_idx, run_elem in enumerate(runs_xml):
            # Check if this run has text
            t_elem = run_elem.find(qn('w:t'))
            if t_elem is not None and t_elem.text:
                print(f"    Run {run_idx}: TEXT = {repr(t_elem.text)}")

            # Check if this run has tab
            tab_elem = run_elem.find(qn('w:tab'))
            if tab_elem is not None:
                print(f"    Run {run_idx}: TAB")

            # Check if this run has math
            math_elem = run_elem.find(qn('m:oMath'))
            if math_elem is not None:
                print(f"    Run {run_idx}: MATH (formula)")

print("\n" + "=" * 80)
