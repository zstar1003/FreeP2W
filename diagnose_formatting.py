"""
诊断 result_final.docx 的格式问题

检查：
1. 哪些段落没有被格式化
2. 哪些字体是 Cambria
3. 哪些段落没有两端对齐
"""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def diagnose_formatting(docx_path):
    """诊断文档格式问题"""

    if not os.path.exists(docx_path):
        print(f"错误: 文件不存在 {docx_path}")
        return

    doc = Document(docx_path)

    print("=" * 80)
    print(f"诊断文件: {docx_path}")
    print("=" * 80)

    cambria_paragraphs = []
    not_justified = []
    not_times_new_roman = []

    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text or len(text) < 20:
            continue

        # 检查是否包含英文
        has_english = bool([c for c in text if c.isalpha() and ord(c) < 128])
        if not has_english:
            continue

        # 检查对齐方式
        if para.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
            not_justified.append({
                'index': para_idx,
                'text': text[:80],
                'alignment': str(para.alignment) if para.alignment else 'None'
            })

        # 检查字体
        for run in para.runs:
            if not run.text.strip():
                continue

            # 检查是否有英文
            run_has_english = bool([c for c in run.text if c.isalpha() and ord(c) < 128])
            if not run_has_english:
                continue

            font_name = run.font.name

            # 记录 Cambria 字体
            if font_name == 'Cambria':
                cambria_paragraphs.append({
                    'index': para_idx,
                    'text': text[:80],
                    'run_text': run.text[:50],
                    'font': font_name
                })

            # 记录非 Times New Roman 字体
            if font_name and font_name != 'Times New Roman':
                not_times_new_roman.append({
                    'index': para_idx,
                    'text': text[:80],
                    'run_text': run.text[:50],
                    'font': font_name
                })

    # 报告结果
    print(f"\n[问题 1] 包含 Cambria 字体的段落: {len(cambria_paragraphs)}")
    if cambria_paragraphs:
        print("-" * 80)
        for item in cambria_paragraphs[:5]:  # 只显示前5个
            print(f"段落 {item['index']}:")
            print(f"  文本: {item['text']}...")
            print(f"  Run: {item['run_text']}")
            print(f"  字体: {item['font']}")
            print()

    print(f"\n[问题 2] 非 Times New Roman 的段落: {len(not_times_new_roman)}")
    if not_times_new_roman:
        print("-" * 80)
        # 按字体分组
        from collections import defaultdict
        by_font = defaultdict(int)
        for item in not_times_new_roman:
            by_font[item['font']] += 1

        print("字体分布:")
        for font, count in sorted(by_font.items(), key=lambda x: -x[1]):
            print(f"  {font}: {count} 次")
        print()

        print("示例（前5个）:")
        for item in not_times_new_roman[:5]:
            print(f"段落 {item['index']}:")
            print(f"  文本: {item['text']}...")
            print(f"  Run: {item['run_text']}")
            print(f"  字体: {item['font']}")
            print()

    print(f"\n[问题 3] 未两端对齐的段落: {len(not_justified)}")
    if not_justified:
        print("-" * 80)
        for item in not_justified[:10]:  # 显示前10个
            print(f"段落 {item['index']}:")
            print(f"  文本: {item['text']}...")
            print(f"  对齐: {item['alignment']}")
            print()

    print("=" * 80)
    print("诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    # 诊断 result_final.docx
    if os.path.exists('result_final.docx'):
        diagnose_formatting('result_final.docx')
    elif os.path.exists('result_formatted.docx'):
        print("未找到 result_final.docx，检查 result_formatted.docx")
        diagnose_formatting('result_formatted.docx')
    elif os.path.exists('result.docx'):
        print("未找到格式化文件，检查原始 result.docx")
        diagnose_formatting('result.docx')
    else:
        print("错误: 未找到任何 docx 文件")
