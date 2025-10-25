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

    # 复制本地模块目录
    local_modules = [
        "doclayout_yolo",
        "pdf2docx",
        "unimernet"
    ]

    for module_name in local_modules:
        src_dir = Path(module_name)
        if src_dir.exists() and src_dir.is_dir():
            dst_dir = pkg_dir / module_name
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"[OK] 已复制模块: {module_name}/ -> freep2w/{module_name}/")
        else:
            print(f"[WARNING] 模块目录不存在: {module_name}/")


    # 创建 __init__.py
    init_file = pkg_dir / "__init__.py"
    with open(init_file, "w", encoding="utf-8") as f:
        f.write('''"""
FreeP2W - Free PDF to Word Converter
"""

__version__ = "1.0.0"

from .hybrid_converter import HybridConverter

# 延迟导入 CLI 函数以避免循环导入
def convert_pdf_to_docx(*args, **kwargs):
    from .cli import convert_pdf_to_docx as _convert
    return _convert(*args, **kwargs)

__all__ = ["HybridConverter", "convert_pdf_to_docx"]
''')
    print(f"[OK] 已创建: freep2w/__init__.py")

    # 创建 cli.py（命令行入口）
    cli_file = pkg_dir / "cli.py"
    with open(cli_file, "w", encoding="utf-8") as f:
        # 读取原始 freep2w.py 的内容
        with open("freep2w.py", "r", encoding="utf-8") as src:
            content = src.read()

        # 修改导入语句 - 使用相对导入
        content = content.replace(
            "from hybrid_converter import HybridConverter",
            "from .hybrid_converter import HybridConverter"
        )

        # 在 convert_pdf_to_docx 函数开头添加模型检查
        insert_pos = content.find('def convert_pdf_to_docx(pdf_path, output_path=None):')
        if insert_pos != -1:
            # 找到函数体开始位置
            body_start = content.find('"""', insert_pos)
            body_end = content.find('"""', body_start + 3) + 3

            # 插入模型检查代码
            model_check = '''

    # 自动检查并下载模型
    try:
        from .model_downloader import check_and_download_models
        print_info("正在检查模型文件...")
        yolo_path, cfg_path = check_and_download_models()
    except Exception as e:
        print(f"[警告] 模型检查失败: {e}")
        print("[INFO] 将使用默认路径继续...")
    '''
            content = content[:body_end] + model_check + content[body_end:]

        f.write(content)
    print(f"[OK] 已创建: freep2w/cli.py (已添加自动模型下载)")

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
    print("│   ├── cli.py (已添加自动模型下载)")
    print("│   ├── hybrid_converter.py")
    print("│   ├── post_format_english_body.py")
    print("│   ├── model_downloader.py")
    print("│   ├── demo.yaml")
    print("│   ├── doclayout_yolo/      # YOLO 模块")
    print("│   ├── pdf2docx/             # PDF2DOCX 模块")
    print("│   ├── unimernet/            # UniMERNet 模块")
    print("│   └── weights/")
    print("│       └── doclayout_yolo_docstructbench_imgsz1024.pt")
    print("├── setup.py")
    print("├── pyproject.toml")
    print("├── MANIFEST.in")
    print("├── README.md")
    print("└── LICENSE")

    print("\n下一步:")
    print("1. 更新 pyproject.toml 的 packages 配置（自动包含子模块）")
    print("2. 测试包: python -m pip install -e .")
    print("3. 测试 CLI: freep2w test.pdf -o output.docx")
    print("4. 构建: python -m build")
    print("5. 上传: twine upload dist/*")


if __name__ == "__main__":
    create_package_structure()
