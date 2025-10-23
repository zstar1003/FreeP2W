"""
测试改进的 hybrid_converter - 使用保留 run 结构的版本
"""

from hybrid_converter import HybridConverter

print("=" * 80)
print("测试改进的 Hybrid Converter - Run 结构保留版本")
print("=" * 80)

# 输入输出文件
pdf_path = "test_files/2503.20314v2.pdf"
output_docx = "result_improved.docx"

print(f"\nInput PDF: {pdf_path}")
print(f"Output DOCX: {output_docx}")
print("\n" + "=" * 80)

# 创建转换器
converter = HybridConverter(
    yolo_model_path="weights/doclayout_yolo_docstructbench_imgsz1024.pt",
    unimernet_cfg_path="demo.yaml"
)

# 转换
print("\n[开始转换]")
converter.convert(
    pdf_path=pdf_path,
    docx_path=output_docx
)

print("\n" + "=" * 80)
print("转换完成！")
print("=" * 80)
print(f"\n输出文件: {output_docx}")
print("\n请检查：")
print("  1. 公式是否正确插入")
print("  2. run 结构是否保留（应该看到 'Preserved runs' 消息）")
print("  3. 段落数量和 run 数量是否更接近 smallpdf")
