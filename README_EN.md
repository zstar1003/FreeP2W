#FreeP2W

<div align="center"> 
<h4> 
<a href="README.md">🇨🇳 Chinese</a> 
<span> | </span> 
<a href="README_EN.md">🇬🇧 English</a> 
</h4>
</div>

## Introduction

FreeP2W This PDF to Word conversion tool leverages pdf2docx and incorporates DocLayout and UniMERNet to achieve better recognition of images and mathematical formulas.

## Quick Start

### System Requirements

- Python 3.8 or higher
- Windows / Linux / macOS
- At least 4GB of available disk space (for storing model files)

### Installation

#### Method 1: Install using uv

```bash
uv add freep2w
```

#### Method 2: Install from PyPI

```bash
pip install freep2w
```

#### Method 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/zstar1003/FreeP2W.git
cd FreeP2W

# Install dependencies
pip install -e .
```

### First Run

On the first run, FreeP2W will automatically download the required model files:

- **YOLO model** (~39 MB): Document layout detection model
- **UniMERNet Model** (~1.6 GB): Mathematical Formula Recognition Model

The model file will be downloaded to the user directory:

- Windows: `C:\Users\<username>\.freep2w\weights\`
- Linux/Mac: `~/.freep2w/weights/`

---

## Usage

#### Basic Usage

```bash
# Convert a PDF file (output file name automatically generated)

freep2w input.pdf

# Specify output file name
freep2w input.pdf -o output.docx

# Full path example
freep2w /path/to/input.pdf -o /path/to/output.docx
```

#### Command Line Parameters

```
freep2w [-h] [-o OUTPUT] [-v] input

Positional Parameters:

input: Input PDF file path

Optional Parameters:

-h, --help: Display help information

-o OUTPUT, --output OUTPUT
Output DOCX file path (optional)
-v, --version displays the version number
```

### Python API

```python
from freep2w.cli import convert_pdf_to_docx

# Convert PDF file
success = convert_pdf_to_docx(
pdf_path='input.pdf',
output_path='output.docx'
)

if success:
print("Conversion successful!")
else:
print("Conversion failed!")
```

### Workflow

1. **Document Analysis**: Use DocLayout-YOLO to detect layout elements (text, images, formulas, tables) in the PDF.
2. **Formula Recognition**: Use UniMERNet to recognize the detected formula areas and convert them to MathML.
3. **Content Extraction**: Use pdf2docx to extract text, tables, and other content.
4. **Document Synthesis**: Combine all recognition results to generate the final document. DOCX file

## Contribution Guidelines

Contributions, bug reports, and suggestions are welcome!

### How to Contribute

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Report an Issue

Please submit an issue report on [GitHub Issues](https://github.com/zstar1003/FreeP2W/issues).

Before submitting, please ensure the following:

- Search to see if similar issues have already been reported
- Provide detailed error information and steps to reproduce the issue
- Include system environment information (OS, Python version, etc.)

---

## Acknowledgements

This project uses the following open source projects:

- [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO) - Document layout detection
- [UniMERNet](https://github.com/opendatalab/UniMERNet) - Mathematical formula recognition
- [pdf2docx](https://github.com/dothinking/pdf2docx) - PDF to DOCX conversion
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF document processing

Thanks to these excellent open source projects!

