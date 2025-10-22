"""
Test to check the actual rendering of formulas in Word document
"""
from docx import Document
from docx.oxml.ns import qn
import zipfile
from lxml import etree

docx_path = "test_files/result_hybrid.docx"

print("Analyzing formula paragraphs in detail...\n")
print("=" * 80)

doc = Document(docx_path)

for idx, para in enumerate(doc.paragraphs):
    para_xml_str = para._element.xml.decode('utf-8') if isinstance(para._element.xml, bytes) else str(para._element.xml)

    if 'm:oMath' in para_xml_str and idx in [36, 37, 42]:
        print(f"\n【Paragraph {idx}】")
        print(f"  Para text (repr): {repr(para.text)}")
        print(f"  Para text length: {len(para.text)}")
        print(f"  Alignment: {para.alignment}")

        # Check tab stops
        pPr = para._element.get_or_add_pPr()
        tabs = pPr.find(qn('w:tabs'))

        if tabs is not None:
            print(f"\n  Tab stops:")
            for tab in tabs:
                tab_pos = tab.get(qn('w:pos'))
                tab_val = tab.get(qn('w:val'))
                if tab_pos:
                    inches = int(tab_pos) / 1440.0
                    print(f"    - Type: {tab_val}, Position: {inches:.2f}\" ({tab_pos} twips)")

        # Check all runs
        print(f"\n  Runs ({len(para.runs)} total):")
        runs_xml = para._element.findall(qn('w:r'))

        for run_idx, run_elem in enumerate(runs_xml):
            print(f"\n    Run {run_idx}:")

            # Check for tab
            has_tab = run_elem.find(qn('w:tab')) is not None
            if has_tab:
                print(f"      [TAB] Has tab element")

            # Check for text
            t_elem = run_elem.find(qn('w:t'))
            if t_elem is not None and t_elem.text:
                print(f"      [TEXT] Text: {repr(t_elem.text)}")

            # Check for math
            math_elem = run_elem.find(qn('m:oMath'))
            if math_elem is not None:
                # Get first few characters of math content
                math_str = etree.tostring(math_elem, encoding='unicode')[:200]
                print(f"      [MATH] Math element found")

print("\n" + "=" * 80)

# Also check the raw XML structure
print("\n\nRaw XML check for paragraph 36:")
print("=" * 80)

with zipfile.ZipFile(docx_path, 'r') as zip_ref:
    with zip_ref.open('word/document.xml') as doc_xml:
        content = doc_xml.read().decode('utf-8')

        # Find paragraph 36 area (rough search)
        import re

        # Look for pattern with tab and equation number
        pattern = r'<w:p[^>]*>.*?<w:tab/>.*?<m:oMath>.*?</m:oMath>.*?<w:tab/>.*?\(1\).*?</w:p>'
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            print("Found formula paragraph pattern:")
            print(matches[0][:500])
        else:
            print("Pattern not found. Searching for any paragraph with (1):")
            pattern2 = r'<w:p[^>]*>.*?\(1\).*?</w:p>'
            matches2 = re.findall(pattern2, content, re.DOTALL)
            if matches2:
                print(matches2[0][:500])

print("=" * 80)
