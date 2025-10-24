"""
详细诊断 - 检查为什么段落没被格式化
"""

from docx import Document
import os


def detailed_diagnose(docx_path):
    """详细诊断段落"""

    if not os.path.exists(docx_path):
        print(f"文件不存在: {docx_path}")
        return

    doc = Document(docx_path)

    print("=" * 80)
    print(f"详细诊断: {docx_path}")
    print("=" * 80)

    # 检查所有包含英文且长度>20的段落
    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        if len(text) < 20:
            continue

        # 检查是否有英文
        has_english = bool([c for c in text if c.isalpha() and ord(c) < 128])
        if not has_english:
            continue

        # 检查对齐方式
        alignment = str(para.alignment) if para.alignment else 'None'

        # 检查是否包含数学公式
        has_math = 'oMath' in para._element.xml if hasattr(para, '_element') else False

        # 检查字体
        font_info = []
        for run in para.runs[:3]:  # 只检查前3个run
            if run.text.strip():
                font_name = run.font.name if run.font.name else 'None'
                font_size = f"{run.font.size.pt}pt" if run.font.size else 'None'
                font_info.append(f"{font_name} {font_size}")

        # 只显示未对齐的段落
        if alignment != "JUSTIFY (3)":
            print(f"\n段落 {para_idx}:")
            print(f"  文本: {text[:80]}...")
            print(f"  对齐: {alignment}")
            print(f"  包含公式: {has_math}")
            if font_info:
                print(f"  字体: {', '.join(font_info)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # 依次检查各个文件
    for filename in ['result_formatted.docx', 'result_final.docx', 'result.docx']:
        if os.path.exists(filename):
            detailed_diagnose(filename)
            break
    else:
        print("未找到任何docx文件")
