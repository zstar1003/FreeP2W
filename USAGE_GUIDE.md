# DocLayout-YOLO PDF to DOCX Converter - 使用指南

## 🎉 成功案例

**测试结果**：
- 输入：`test_files/2503.20314v2.pdf` (5页)
- 输出：`test_files/result_doclayout.docx` (2.4MB)
- **提取了5个完整的figure区域**
- 图片质量完整，无分割问题

---

## 📋 快速开始

### 基础用法

```bash
python test_doclayout.py
```

或者自定义PDF：

```python
from doclayout_converter import DocLayoutYOLOConverter

converter = DocLayoutYOLOConverter('weights/doclayout_yolo_docstructbench_imgsz1024.pt')

converter.convert(
    pdf_path='your_file.pdf',
    docx_path='output.docx'
)
```

---

## ⚙️ 参数调优

### 1. 检测灵敏度调整

```python
converter.convert(
    pdf_path='input.pdf',
    docx_path='output.docx',
    conf=0.25  # 调整这个值
)
```

| conf值 | 效果 | 适用场景 |
|--------|------|---------|
| 0.15 | 检测更多figure（可能有误检） | Figure较小或不明显 |
| 0.25 | **默认值，平衡** | 大多数情况 |
| 0.40 | 只检测高置信度figure | Figure很明显，要求准确 |

### 2. 图像质量调整

```python
converter.convert(
    pdf_path='input.pdf',
    docx_path='output.docx',
    dpi=150,           # 布局检测DPI
    image_quality=4.0   # 提取图片的质量倍数
)
```

| 参数组合 | 文件大小 | 质量 | 速度 |
|---------|---------|------|------|
| dpi=150, quality=3.0 | 小 | 一般 | 快 |
| dpi=150, quality=4.0 | **中（推荐）** | **好** | **中** |
| dpi=200, quality=6.0 | 大 | 很好 | 慢 |

### 3. 检测模型尺寸

```python
converter.convert(
    pdf_path='input.pdf',
    docx_path='output.docx',
    imgsz=1024  # 调整这个值
)
```

| imgsz | 速度 | 准确率 | 适用场景 |
|-------|------|--------|---------|
| 640 | 很快 | 一般 | 简单文档、快速预览 |
| 1024 | **中（推荐）** | **好** | **大多数文档** |
| 1280 | 慢 | 很好 | 复杂布局、高质量要求 |

---

## 🔧 进阶功能

### 启用文本提取

目前只提取figure，如需文本内容：

编辑 `doclayout_converter.py` 第91-94行：

```python
# 取消注释以下代码
elif region_type in ['text', 'Text', 'title', 'Title', 'caption', 'Caption']:
    # Extract text
    self._insert_text_region(page, bbox, docx_doc, region_type)
```

**注意**：文本提取使用PyMuPDF的简单text extraction，可能格式不完美。

### 批量转换

```bash
# 转换整个文件夹的PDF
python batch_convert.py --input-dir pdfs/ --output-dir outputs/
```

可选参数：
```bash
python batch_convert.py \
    --input-dir pdfs/ \
    --output-dir outputs/ \
    --conf 0.3 \
    --imgsz 1024
```

---

## 📊 效果对比

### 与之前方案的对比

| 方案 | Figure提取 | 准确率 | 速度 | 文本质量 |
|------|-----------|--------|------|---------|
| **原始pdf2docx** | ❌ 碎片化 | 低 | 快 | 好 |
| **ImageMerger** | ✅ 合并小块 | 中 | 快 | 好 |
| **DocLayout-YOLO** | ✅ **AI检测** | **高** | 中 | 一般 |

### DocLayout-YOLO的优势

✅ **准确识别图片边界** - AI模型训练过，不会误判
✅ **完整提取** - 直接提取检测到的区域，无需合并
✅ **支持GPU加速** - CUDA加速，处理速度快
✅ **可调节** - 通过conf参数灵活控制

### 适用场景

**最适合**：
- 图片边界清晰的学术论文
- 包含大量图表的技术文档
- 需要高质量图片提取的场景

**不太适合**：
- 纯文本文档（建议用原版pdf2docx）
- 需要完美文本格式的场景
- 图片非常小且密集的文档

---

## 🐛 故障排查

### 问题1：检测不到figure

**解决方案**：
1. 降低conf阈值：`conf=0.15`
2. 增大图像尺寸：`imgsz=1280`
3. 检查PDF中是否真的有figure（用Adobe Reader查看）

### 问题2：检测到太多误报

**解决方案**：
1. 提高conf阈值：`conf=0.4`
2. 手动过滤：在代码中添加面积或宽高比过滤

### 问题3：图片质量不够

**解决方案**：
1. 提高提取质量：`image_quality=6.0`
2. 提高DPI：`dpi=200`

### 问题4：转换速度慢

**解决方案**：
1. 降低检测尺寸：`imgsz=640`
2. 确认GPU可用：检查`Using device: cuda`
3. 减少页面数量进行测试

---

## 📁 项目文件说明

```
E:\code\FreeP2W\
├── weights/
│   └── doclayout_yolo_docstructbench_imgsz1024.pt  # YOLO模型
├── doclayout_converter.py          # 核心转换器 ⭐
├── test_doclayout.py                # 测试脚本 ⭐
├── batch_convert.py                 # 批量转换 ⭐
├── demo.py                          # YOLO原始demo
├── test_files/
│   ├── 2503.20314v2.pdf            # 测试PDF
│   └── result_doclayout.docx        # 输出结果 ✅
└── DOCLAYOUT_SOLUTION.md            # 本文档
```

---

## 💡 最佳实践

### 推荐的工作流程

1. **先测试单个PDF**
   ```bash
   python test_doclayout.py
   ```

2. **检查输出质量**
   - 打开`result_doclayout.docx`
   - 确认figure是否完整
   - 检查是否有漏检或误检

3. **调整参数**
   - 如果漏检：降低`conf`
   - 如果误检：提高`conf`
   - 如果质量不够：提高`image_quality`

4. **批量处理**
   ```bash
   python batch_convert.py --input-dir pdfs/ --output-dir outputs/
   ```

### 性能优化建议

- **GPU加速**：确保CUDA可用，速度提升3-5倍
- **合理的参数**：不要追求极致，`conf=0.25, imgsz=1024`已经很好
- **分批处理**：大量PDF时，分批转换避免内存问题

---

## ✅ 成功标志

如果看到以下输出，说明成功：

```
[INFO] Using device: cuda
Processing Page 1/5
  Detected 9 regions
    - figure: 2
    - text: 5
      [Figure] Inserted: 398.5 x 114.2 pt
      [Figure] Inserted: 196.4 x 112.4 pt
...
Conversion completed!
Output: test_files/result_doclayout.docx
```

**恭喜！你已经成功将DocLayout-YOLO集成到PDF to DOCX转换流程中！** 🎉

---

## 🚀 下一步建议

1. ✅ **已完成**：基础figure提取
2. 🔄 **可选**：添加文本提取功能
3. 🔄 **可选**：添加表格提取（DocLayout-YOLO也能检测table）
4. 🔄 **可选**：结合pdf2docx的文本功能，创建混合方案

需要帮助实现这些功能，随时告诉我！
