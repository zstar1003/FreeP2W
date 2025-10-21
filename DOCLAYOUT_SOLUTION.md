# DocLayout-YOLO Integration Status and Solution

## Current Situation

### ✅ Working
- **DocLayout-YOLO**: demo.py可以正常运行，检测figure等布局元素
- **Device**: CUDA GPU可用，速度快
- **Detection Results**: 能成功检测title, plain text, figure, figure_caption等

### ❌ Problem
- **.venv环境中PyMuPDF导入失败**:
  ```
  ImportError: cannot import name '_as_fz_document' from 'pymupdf'
  ```
- 这导致无法使用`import fitz`或pdf2docx的代码
- 所有依赖PyMuPDF的方案都无法运行

## 最佳解决方案

### 方案A：修复PyMuPDF（推荐）⭐⭐⭐⭐⭐

**步骤**:
```bash
# 1. 完全卸载PyMuPDF相关包
pip uninstall pymupdf fitz PyMuPDF -y

# 2. 重新安装PyMuPDF
pip install PyMuPDF

# 3. 测试
python -c "import fitz; print(fitz.version)"
```

**如果成功**，之前创建的所有方案都可以使用：
- `doclayout_converter.py` - 完整的DocLayout-YOLO + pdf2docx集成
- `test_doclayout.py` - 测试脚本

### 方案B：两步法（临时方案）⭐⭐⭐⭐

既然demo.py可以运行，我们可以分两步处理：

**第1步：使用demo.py检测布局**
```bash
# 先将PDF页面导出为图片（手动或用其他工具）
# 然后运行demo.py检测
python demo.py --image-path page_3.png --res-path outputs
```

**第2步：根据检测结果手动提取figure**

我可以创建一个辅助脚本，读取demo.py的输出，然后：
1. 解析YOLO检测结果
2. 找到所有figure区域的坐标
3. 从PDF中提取这些区域
4. 插入到DOCX

### 方案C：创建完全独立的流程⭐⭐⭐

**流程**:
```
PDF → 图片 (手动) → YOLO检测 → 提取figure坐标 → 手动裁剪图片 → 插入DOCX
```

## 我的建议

**强烈建议先尝试方案A - 修复PyMuPDF**

因为：
1. PyMuPDF是pdf2docx的核心依赖，修复后所有功能都能用
2. 你之前运行test_smart_merge.py应该是可以的，说明PyMuPDF曾经工作过
3. 修复后，DocLayout-YOLO集成将完全无缝工作

## 快速诊断

请运行以下命令帮我诊断问题：

```bash
# 1. 检查PyMuPDF安装
pip list | grep -i pymupdf

# 2. 检查import情况
python -c "import sys; print(sys.path)"

# 3. 尝试导入
python -c "import fitz"

# 4. 检查pdf2docx是否能用
python -c "from pdf2docx import Converter; print('OK')"
```

## 如果方案A失败

如果修复PyMuPDF失败，我可以为你创建：

### 选项1：纯手工流程脚本
```python
# 1. 读取demo.py的输出（已标注的图片）
# 2. 解析figure位置
# 3. 生成裁剪坐标列表
# 4. 你手动用PDF工具裁剪
# 5. 脚本组装DOCX
```

### 选项2：使用pdf2image替代PyMuPDF
- 需要先安装：`pip install pdf2image poppler-utils`
- 完全绕开PyMuPDF
- 但会稍微慢一些

## 推荐步骤

**请按顺序尝试**:

1. ✅ **先尝试修复PyMuPDF**（方案A）
2. ⚠️ 如果失败，告诉我错误信息
3. 🔧 我会根据错误调整方案

---

## 快速测试命令

修复PyMuPDF后，立即测试：

```bash
# 测试DocLayout-YOLO转换器
python -c "
from doclayout_converter import DocLayoutYOLOConverter

converter = DocLayoutYOLOConverter('weights/doclayout_yolo_docstructbench_imgsz1024.pt')
converter.convert(
    pdf_path='test_files/2503.20314v2.pdf',
    docx_path='test_files/result_doclayout.docx',
    imgsz=1024,
    conf=0.25
)
"
```

如果成功，你会看到：
- 每页检测到的布局元素
- Figure区域被提取并插入DOCX
- 最终生成`result_doclayout.docx`

---

## 我需要你的反馈

请告诉我：
1. **方案A（修复PyMuPDF）的结果** - 成功还是失败？错误信息是什么？
2. **你更倾向哪个方案** - A/B/C？

根据你的反馈，我会立即提供相应的完整实现！
