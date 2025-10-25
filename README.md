# FreeP2W 

<div align="center">
  <h4>
    <a href="README.md">🇨🇳 中文</a>
    <span> | </span>
    <a href="README_EN.md">🇬🇧 English</a>
  </h4>
</div>

## 简介

FreeP2W 是一款将 PDF 到 Word 转换工具，在 pdf2docx 的基础上，引入了 DocLayout 和 UniMERNet 实现对图片和数学公式更好的识别效果。

## 快速开始

### 系统要求

- Python 3.8 或更高版本
- Windows / Linux / macOS
- 至少 4GB 可用磁盘空间（用于存储模型文件）

### 安装

#### 方式 1: 使用 uv 进行安装

```bash
uv add freep2w
```

#### 方式 2: 从 PyPI 安装

```bash
pip install freep2w
```

#### 方式 3: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/zstar1003/FreeP2W.git
cd FreeP2W

# 安装依赖
pip install -e .
```

### 首次运行

首次运行时，FreeP2W 会自动下载所需的模型文件：

- **YOLO 模型** (~39 MB): 文档布局检测模型
- **UniMERNet 模型** (~1.6 GB): 数学公式识别模型

模型文件会被下载到用户目录：

- Windows: `C:\Users\<用户名>\.freep2w\weights\`
- Linux/Mac: `~/.freep2w/weights/`

---

## 使用方法

#### 基本用法

```bash
# 转换 PDF 文件（输出文件名自动生成）
freep2w input.pdf

# 指定输出文件名
freep2w input.pdf -o output.docx

# 完整路径示例
freep2w /path/to/input.pdf -o /path/to/output.docx
```

#### 命令行参数

```
freep2w [-h] [-o OUTPUT] [-v] input

位置参数:
  input                 输入 PDF 文件路径

可选参数:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        输出 DOCX 文件路径（可选）
  -v, --version         显示版本号
```

### Python API

```python
from freep2w.cli import convert_pdf_to_docx

# 转换 PDF 文件
success = convert_pdf_to_docx(
    pdf_path='input.pdf',
    output_path='output.docx'
)

if success:
    print("转换成功！")
else:
    print("转换失败！")
```

### 工作流程

1. **文档分析**: 使用 DocLayout-YOLO 检测 PDF 中的布局元素（文本、图片、公式、表格）
2. **公式识别**: 对检测到的公式区域使用 UniMERNet 进行识别并转换为 MathML
3. **内容提取**: 使用 pdf2docx 提取文本、表格等内容
4. **文档合成**: 将所有识别结果合并生成最终的 DOCX 文件

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题

请在 [GitHub Issues](https://github.com/zstar1003/FreeP2W/issues) 提交问题报告。

提交前请确认：

- 搜索是否有相同的问题已被报告
- 提供详细的错误信息和复现步骤
- 附上系统环境信息（操作系统、Python 版本等）

---

## 致谢

本项目使用了以下开源项目：

- [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO) - 文档布局检测
- [UniMERNet](https://github.com/opendatalab/UniMERNet) - 数学公式识别
- [pdf2docx](https://github.com/dothinking/pdf2docx) - PDF 到 DOCX 转换
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF 文档处理

感谢这些优秀的开源项目！
