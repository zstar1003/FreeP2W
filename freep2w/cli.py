"""
FreeP2W - Free PDF to Word Converter
Command-line tool with clean output
"""

import sys
import os
import warnings
import logging
from pathlib import Path

# Add project root to sys.path to ensure local modules are found
# This is necessary when running via entry point
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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

    # 自动检查并下载模型
    yolo_path = None
    cfg_path = None
    try:
        from .model_downloader import check_and_download_models
        print_info("正在检查模型文件...")
        yolo_path, cfg_path = check_and_download_models()
        print(f"[DEBUG] YOLO路径: {yolo_path}")
        print(f"[DEBUG] 配置路径: {cfg_path}")
    except Exception as e:
        print(f"[警告] 模型检查失败: {e}")
        print("[INFO] 将使用默认路径继续...")
        import traceback
        traceback.print_exc()
    
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
            from .hybrid_converter import HybridConverter
            from pdf2docx import Converter

            # 恢复输出
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print_info("开始转换 PDF...")

            # 转换 PDF（使用下载的模型路径）
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            # 使用下载的模型路径，如果没有则使用默认相对路径
            if yolo_path and cfg_path:
                converter = HybridConverter(
                    yolo_model_path=yolo_path,
                    unimernet_cfg_path=cfg_path
                )
            else:
                # Fallback: 使用项目目录的相对路径
                converter = HybridConverter(
                    yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
                    unimernet_cfg_path="demo.yaml"
                )

            converter.convert(pdf_path=pdf_path, docx_path=output_path)

            # converter = Converter(pdf_path)
            # converter.convert(output_path)

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print_info("PDF 转换完成")

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
