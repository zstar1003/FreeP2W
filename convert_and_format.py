"""
完整的 PDF 到 DOCX 转换工作流

步骤：
1. 使用 hybrid_converter 转换 PDF（保留公式）
2. 使用 post_format_english_body 统一英文正文格式

使用方法：
    python convert_and_format.py <pdf_path> <output_path>

示例：
    python convert_and_format.py test_files/2503.20314v2.pdf result_final.docx
"""

import sys
import os
from hybrid_converter import HybridConverter
from post_format_improved import format_english_body_text_improved
from docx.enum.text import WD_ALIGN_PARAGRAPH


def convert_and_format(pdf_path, final_output_path,
                       temp_output_path="temp_converted.docx",
                       target_font='Times New Roman',
                       target_size=10.0):
    """
    完整的转换和格式化流程

    Args:
        pdf_path: 输入 PDF 文件路径
        final_output_path: 最终输出 DOCX 文件路径
        temp_output_path: 临时转换文件路径
        target_font: 目标字体（默认 Times New Roman）
        target_size: 目标字体大小（默认 10pt）
    """
    print("=" * 80)
    print("PDF 到 DOCX 完整转换流程")
    print("=" * 80)
    print(f"\n输入 PDF: {pdf_path}")
    print(f"输出 DOCX: {final_output_path}")
    print(f"\n格式设置:")
    print(f"  英文正文字体: {target_font}")
    print(f"  英文正文大小: {target_size}pt")
    print(f"  英文正文对齐: 两端对齐")
    print("\n" + "=" * 80)

    # 检查输入文件
    if not os.path.exists(pdf_path):
        print(f"\n[错误] PDF 文件不存在: {pdf_path}")
        return False

    # 步骤 1: PDF 转 DOCX（保留公式）
    print("\n" + "=" * 80)
    print("[步骤 1/2] PDF 转 DOCX（保留公式识别）")
    print("=" * 80)

    try:
        converter = HybridConverter(
            yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
            unimernet_cfg_path="demo.yaml"
        )

        converter.convert(
            pdf_path=pdf_path,
            docx_path=temp_output_path
        )

        print(f"\n[完成] 初步转换完成: {temp_output_path}")

    except Exception as e:
        print(f"\n[错误] PDF 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 步骤 2: 格式化英文正文
    print("\n" + "=" * 80)
    print("[步骤 2/2] 格式化英文正文")
    print("=" * 80)

    try:
        format_english_body_text_improved(
            input_path=temp_output_path,
            output_path=final_output_path,
            target_font=target_font,
            target_size=target_size,
            target_alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        )

        print(f"\n[完成] 格式化完成: {final_output_path}")

    except Exception as e:
        print(f"\n[错误] 格式化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 清理临时文件（可选）
    try:
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
            print(f"\n[清理] 已删除临时文件: {temp_output_path}")
    except:
        pass

    # 完成
    print("\n" + "=" * 80)
    print("[成功] 转换和格式化全部完成！")
    print("=" * 80)
    print(f"\n最终输出文件: {final_output_path}")
    print("\n特点:")
    print("  - 公式完美保留（DocLayout-YOLO + UniMERNet）")
    print(f"  - 英文正文统一为 {target_font} {target_size}pt")
    print("  - 英文正文两端对齐")
    print("  - 标题、图表标题、公式保持原格式")
    print("=" * 80)

    return True


if __name__ == "__main__":
    # 命令行参数
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python convert_and_format.py <pdf_path> <output_path>")
        print("\n示例:")
        print("  python convert_and_format.py test_files/2503.20314v2.pdf result_final.docx")
        print("\n或直接运行使用默认参数:")
        pdf_path = "test_files/2503.20314v2.pdf"
        output_path = "result_final.docx"
    else:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2]

    # 执行完整流程
    success = convert_and_format(
        pdf_path=pdf_path,
        final_output_path=output_path,
        target_font='Times New Roman',
        target_size=10.0
    )

    if success:
        print("\n全部完成！可以打开文件查看效果。")
    else:
        print("\n转换过程中出现错误，请检查日志。")
        sys.exit(1)
