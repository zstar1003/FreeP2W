"""
从 PDF 到 DOCX 转换

使用方法：
    python convert_and_format.py <pdf_path> <output_path>

示例：
    python convert_and_format.py test_files/2503.20314v2.pdf result_final.docx
"""

import sys
import os
from hybrid_converter import HybridConverter
from pdf2docx import Converter


def convert_and_format(pdf_path, final_output_path,
                       temp_output_path="temp_converted.docx"):
    """
    完整的转换和格式化流程

    Args:
        pdf_path: 输入 PDF 文件路径
        final_output_path: 最终输出 DOCX 文件路径
        temp_output_path: 临时转换文件路径
        target_font: 目标字体（默认 Times New Roman）
        target_size: 目标字体大小（默认 10pt）
    """

    # 检查输入文件
    if not os.path.exists(pdf_path):
        print(f"\n[错误] PDF 文件不存在: {pdf_path}")
        return False

    # 步骤 1: PDF 转 DOCX（保留公式）
    print("\n" + "=" * 80)
    print("[步骤 1/2] PDF 转 DOCX（保留公式识别）")
    print("=" * 80)

    try:
        # converter = HybridConverter(
        #     yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
        #     unimernet_cfg_path="demo.yaml"
        # )
        
        converter = Converter()

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
        final_output_path=output_path
    )

    if success:
        print("\n全部完成！可以打开文件查看效果。")
    else:
        print("\n转换过程中出现错误，请检查日志。")
        sys.exit(1)
