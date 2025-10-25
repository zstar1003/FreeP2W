"""
Organize files for PyPI distribution
将项目文件组织成 PyPI 包结构
"""

import os
import shutil
from pathlib import Path

def create_package_structure():
    """创建 freep2w 包目录结构"""

    print("[INFO] 开始组织文件结构...")

    # 创建包目录
    pkg_dir = Path("freep2w")
    pkg_dir.mkdir(exist_ok=True)

    # 需要复制到包目录的文件
    files_to_copy = [
        "hybrid_converter.py",
        "post_format_english_body.py",
        "model_downloader.py",
        "demo.yaml",
    ]

    # 复制文件
    for filename in files_to_copy:
        src = Path(filename)
        if src.exists():
            dst = pkg_dir / filename
            shutil.copy2(src, dst)
            print(f"[OK] 已复制: {filename} -> freep2w/{filename}")
        else:
            print(f"[WARNING] 文件不存在: {filename}")

    # 创建 __init__.py
    init_file = pkg_dir / "__init__.py"
    with open(init_file, "w", encoding="utf-8") as f:
        f.write('''"""
FreeP2W - Free PDF to Word Converter
"""

__version__ = "1.0.0"

from .hybrid_converter import HybridConverter
from .cli import convert_pdf_to_docx

__all__ = ["HybridConverter", "convert_pdf_to_docx"]
''')
    print(f"[OK] 已创建: freep2w/__init__.py")

    # 创建 cli.py（命令行入口）
    cli_file = pkg_dir / "cli.py"
    with open(cli_file, "w", encoding="utf-8") as f:
        # 读取原始 freep2w.py 的内容
        with open("freep2w.py", "r", encoding="utf-8") as src:
            content = src.read()

        # 修改导入语句
        content = content.replace(
            "from hybrid_converter import HybridConverter",
            "from .hybrid_converter import HybridConverter"
        )
        content = content.replace(
            "from pdf2docx import Converter",
            "from pdf2docx import Converter"
        )

        f.write(content)
    print(f"[OK] 已创建: freep2w/cli.py")

    # 复制 weights 目录（只复制 YOLO 模型，UniMERNet 太大）
    weights_dir = pkg_dir / "weights"
    weights_dir.mkdir(exist_ok=True)

    yolo_model = Path("weights/doclayout_yolo_docstructbench_imgsz1024.pt")
    if yolo_model.exists():
        shutil.copy2(yolo_model, weights_dir / yolo_model.name)
        print(f"[OK] 已复制: YOLO 模型 (39MB)")
    else:
        print(f"[WARNING] YOLO 模型不存在: {yolo_model}")

    # 创建 .gitignore（排除大文件）
    gitignore = Path(".gitignore")
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Large model files (download separately)
weights/unimernet_small/
*.pth

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temp files
temp_*.docx
*_converted.docx
"""

    with open(gitignore, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print(f"[OK] 已创建: .gitignore")

    print("\n[SUCCESS] 包结构创建完成！")
    print("\n目录结构:")
    print("FreeP2W/")
    print("├── freep2w/")
    print("│   ├── __init__.py")
    print("│   ├── cli.py")
    print("│   ├── hybrid_converter.py")
    print("│   ├── post_format_english_body.py")
    print("│   ├── model_downloader.py")
    print("│   ├── demo.yaml")
    print("│   └── weights/")
    print("│       └── doclayout_yolo_docstructbench_imgsz1024.pt")
    print("├── setup.py")
    print("├── pyproject.toml")
    print("├── MANIFEST.in")
    print("├── README.md")
    print("└── LICENSE")

    print("\n下一步:")
    print("1. 修改 pyproject.toml 中的作者信息和 GitHub 链接")
    print("2. 创建 LICENSE 文件")
    print("3. 测试包: python -m pip install -e .")
    print("4. 构建: python -m build")
    print("5. 上传: twine upload dist/*")


if __name__ == "__main__":
    create_package_structure()
