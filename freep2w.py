"""
FreeP2W - Free PDF to Word Converter
Command-line tool with clean output
"""

import sys
import os
import warnings
import logging

# 禁用所有警告
warnings.filterwarnings('ignore')

# 配置日志只显示关键信息
logging.basicConfig(
    level=logging.CRITICAL,  # 只显示严重错误
    format='%(message)s'
)

# 禁用第三方库的日志
logging.getLogger('pdf2docx').setLevel(logging.CRITICAL)
logging.getLogger('fitz').setLevel(logging.CRITICAL)
logging.getLogger('PIL').setLevel(logging.CRITICAL)


def print_info(message):
    """打印 [INFO] 信息"""
    print(f"[INFO] {message}")


def print_save(filepath):
    """打印 [保存] 信息"""
    print(f"[保存] 已保存到: {filepath}")


def convert_pdf_to_docx(pdf_path, output_path=None):
    """
    转换 PDF 到 DOCX

    Args:
        pdf_path: PDF 文件路径
        output_path: 输出 DOCX 路径（可选）
    """
    # 验证输入文件
    if not os.path.exists(pdf_path):
        print(f"[错误] PDF 文件不存在: {pdf_path}")
        return False

    # 确定输出路径
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"{base_name}_converted.docx"

    try:
        # 导入转换器（延迟导入以加快启动速度）
        print_info("正在加载转换器...")

        # 重定向标准输出到空
        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            from hybrid_converter import HybridConverter
            from post_format_english_body import format_english_body_text_improved
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            # 恢复输出
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print_info("开始转换 PDF...")

            # 临时文件
            temp_path = "temp_converted.docx"

            # 步骤 1: 转换 PDF
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            converter = HybridConverter(
                yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
                unimernet_cfg_path="demo.yaml"
            )
            converter.convert(pdf_path=pdf_path, docx_path=temp_path)

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print_info("PDF 转换完成")
            print_info("开始格式化文档...")

            # 步骤 2: 格式化
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            format_english_body_text_improved(
                input_path=temp_path,
                output_path=output_path,
                target_font='Times New Roman',
                target_size=10.0,
                target_alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
            )

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print_info("格式化完成")

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            print_save(output_path)
            return True

        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            print(f"[错误] 转换失败: {e}")
            return False

    except Exception as e:
        print(f"[错误] 加载失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='FreeP2W - Free PDF to Word Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  freep2w input.pdf                    # 转换为 input_converted.docx
  freep2w input.pdf -o output.docx     # 指定输出文件名
  freep2w test.pdf -o result.docx      # 完整示例
        """
    )

    parser.add_argument('input', help='输入 PDF 文件路径')
    parser.add_argument('-o', '--output', help='输出 DOCX 文件路径（可选）')
    parser.add_argument('-v', '--version', action='version', version='FreeP2W 1.0')

    args = parser.parse_args()

    # 执行转换
    success = convert_pdf_to_docx(args.input, args.output)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
