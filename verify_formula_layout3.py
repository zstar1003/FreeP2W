"""
Verify formula layout - check all runs including empty ones
"""
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

docx_path = "test_files/result_hybrid.docx"

doc = Document(docx_path)

print("Checking formula paragraph structure (detailed)...\n")
print("=" * 80)

for idx, para in enumerate(doc.paragraphs):
    # Look for paragraphs with math zones (formulas)
    para_xml_bytes = para._element.xml
    para_xml_str = para_xml_bytes.decode('utf-8') if isinstance(para_xml_bytes, bytes) else str(para_xml_bytes)

    if 'm:oMath' in para_xml_str and idx in [36, 37, 42]:
        print(f"\nParagraph {idx}:")
        print(f"  Text preview: {para.text[:80]}")

        # Get all w:r (run) elements in order
        runs_xml = para._element.findall(qn('w:r'))
        print(f"  Number of w:r elements: {len(runs_xml)}")

        for run_idx, run_elem in enumerate(runs_xml):
            print(f"    Run {run_idx}:")

            # Check all child elements
            for child in run_elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

                if tag == 't':  # Text
                    print(f"      - <w:t>: {repr(child.text)}")
                elif tag == 'tab':  # Tab
                    print(f"      - <w:tab>")
                elif tag == 'oMath':  # Math
                    print(f"      - <m:oMath>: (formula)")
                else:
                    print(f"      - <{tag}>")

print("\n" + "=" * 80)
