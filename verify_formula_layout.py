"""
Verify formula layout - check tab stops and equation number positioning
"""
from docx import Document
from docx.oxml.ns import qn

docx_path = "test_files/result_hybrid.docx"

doc = Document(docx_path)

print("Checking formula paragraphs with equation numbers...\n")
print("=" * 80)

for idx, para in enumerate(doc.paragraphs):
    # Look for paragraphs with math zones (formulas)
    para_xml = para._element.xml.decode('utf-8') if isinstance(para._element.xml, bytes) else str(para._element.xml)

    if 'm:oMath' in para_xml and '(' in para.text:
        print(f"\nParagraph {idx}:")
        print(f"  Text: {para.text[:100]}")
        print(f"  Alignment: {para.alignment}")

        # Check tab stops
        pPr = para._element.get_or_add_pPr()
        tabs = pPr.find(qn('w:tabs'))

        if tabs is not None:
            print(f"  Tab stops found:")
            for tab in tabs:
                tab_pos = tab.get(qn('w:pos'))
                tab_val = tab.get(qn('w:val'))
                if tab_pos:
                    inches = int(tab_pos) / 1440.0
                    print(f"    - {tab_val} at {inches:.2f} inches ({tab_pos} twips)")
        else:
            print(f"  No tab stops found")

        # Check runs
        print(f"  Runs ({len(para.runs)}):")
        for run_idx, run in enumerate(para.runs):
            run_text = run.text
            if run_text:
                display_text = repr(run_text) if '\t' in run_text else run_text
                print(f"    {run_idx}: {display_text}")

print("\n" + "=" * 80)
