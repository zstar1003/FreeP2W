"""
Verify updated table layout with new column widths
"""
from docx import Document
from docx.oxml.ns import qn

docx_path = "test_files/result_hybrid.docx"

doc = Document(docx_path)

print("Checking formula table properties...\n")
print("=" * 80)

table_count = 0
for idx, table in enumerate(doc.tables):
    # Check if this is a formula table (1 row, 3 columns)
    if len(table.rows) == 1 and len(table.columns) == 3:
        table_count += 1
        row = table.rows[0]

        print(f"\nFormula Table #{table_count}:")

        # Check table width
        tbl_elem = table._element
        tblPr = tbl_elem.find(qn('w:tblPr'))
        if tblPr is not None:
            tblW = tblPr.find(qn('w:tblW'))
            if tblW is not None:
                w_type = tblW.get(qn('w:type'))
                w_val = tblW.get(qn('w:w'))
                print(f"  Table width: type={w_type}, value={w_val}")

            tblInd = tblPr.find(qn('w:tblInd'))
            if tblInd is not None:
                ind_val = tblInd.get(qn('w:w'))
                print(f"  Table indent: {ind_val} twips")

        # Check column widths
        print(f"  Column widths:")
        for col_idx in range(3):
            cell = row.cells[col_idx]
            tcPr = cell._element.find(qn('w:tcPr'))
            if tcPr is not None:
                tcW = tcPr.find(qn('w:tcW'))
                if tcW is not None:
                    w_type = tcW.get(qn('w:type'))
                    w_val = tcW.get(qn('w:w'))

                    # Convert to percentage
                    if w_type == 'pct':
                        pct = int(w_val) / 50.0  # 5000 = 100%
                        print(f"    Col {col_idx}: {w_val} ({pct:.1f}%)")
                    else:
                        print(f"    Col {col_idx}: type={w_type}, value={w_val}")

        # Check content
        cell1_text = row.cells[1].text.strip()
        cell2_text = row.cells[2].text.strip()

        cell1_xml = row.cells[1]._element.xml.decode('utf-8') if isinstance(row.cells[1]._element.xml, bytes) else str(row.cells[1]._element.xml)
        has_math = 'm:oMath' in cell1_xml

        print(f"  Content: Formula={'Yes' if has_math else 'No'}, Number='{cell2_text}'")

print(f"\n" + "=" * 80)
print(f"Total formula tables: {table_count}")
print("=" * 80)
