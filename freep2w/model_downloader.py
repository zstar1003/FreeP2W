"""
Model downloader for FreeP2W
Automatically downloads UniMERNet model on first run
"""

import os
import sys
import urllib.request
from pathlib import Path
import zipfile
import shutil


def get_model_dir():
    """Get the directory where models should be stored"""
    # For installed package, use user's home directory
    home = Path.home()
    model_dir = home / ".freep2w" / "weights"
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


def download_file(url, dest_path, description="Downloading"):
    """Download file with progress bar"""
    print(f"[INFO] {description}...")

    # Convert Path to string for urllib
    dest_path = str(dest_path)

    def progress_hook(count, block_size, total_size):
        if total_size > 0:
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r[INFO] 下载进度: {percent}%")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()  # New line after download
        print(f"[INFO] 下载完成: {dest_path}")
    except Exception as e:
        print(f"\n[错误] 下载失败: {e}")
        raise


def check_and_download_models():
    """
    Check if models exist, download if needed
    Returns: (yolo_model_path, unimernet_cfg_path)
    """
    model_dir = get_model_dir()

    # Check YOLO model
    yolo_model = model_dir / "doclayout_yolo_docstructbench_imgsz1024.pt"
    if not yolo_model.exists():
        try:
            YOLO_MODEL_URL = "https://github.com/zstar1003/FreeP2W/releases/download/v0.0.1/doclayout_yolo_docstructbench_imgsz1024.pt"
            download_file(YOLO_MODEL_URL, yolo_model, "下载 YOLO 模型")
        except Exception as e:
            print(f"[警告] 从 GitHub 下载失败: {e}")
            print("[INFO] 尝试使用包内的模型文件...")
            # Fallback to package's weights directory
            package_model = Path(__file__).parent / "weights" / "doclayout_yolo_docstructbench_imgsz1024.pt"
            if package_model.exists():
                shutil.copy(package_model, yolo_model)
                print(f"[OK] 已从包目录复制模型到: {yolo_model}")
            else:
                print("[ERROR] 包内也找不到模型文件")
                raise FileNotFoundError(f"YOLO 模型不存在: {yolo_model}")

    # Check UniMERNet model
    unimernet_dir = model_dir / "unimernet_small"
    if not unimernet_dir.exists():
        try:
            download_unimernet_model(unimernet_dir)
        except Exception as e:
            print(f"[警告] UniMERNet 模型下载失败: {e}")
            print("[INFO] 将使用项目根目录的 unimernet 模块")
            # Note: The unimernet module is already in sys.path via package installation

    # Check config file
    demo_yaml = model_dir / "demo.yaml"
    unimernet_dir = model_dir / "unimernet_small"

    # Always regenerate config with correct paths
    default_yaml = Path(__file__).parent / "demo.yaml"
    if default_yaml.exists():
        # Read default config
        with open(default_yaml, 'r', encoding='utf-8') as f:
            config_content = f.read()

        # Replace relative paths with absolute paths
        config_content = config_content.replace(
            './weights/unimernet_small',
            str(unimernet_dir).replace('\\', '/')
        )

        # Write updated config
        with open(demo_yaml, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"[OK] 已生成配置文件: {demo_yaml}")
        print(f"[OK] UniMERNet 模型路径: {unimernet_dir}")

    return str(yolo_model), str(demo_yaml)


def download_unimernet_model(dest_dir):
    print("[INFO] 自动下载 UniMERNet 模型...")
    url = "https://github.com/zstar1003/FreeP2W/releases/download/v0.0.1/unimernet_small.zip"
    zip_path = dest_dir.parent / "unimernet_small.zip"
    download_file(url, zip_path, "下载 UniMERNet 模型")

    # Extract to the specific unimernet_small directory
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)  # Extract directly to dest_dir (weights/unimernet_small/)

    zip_path.unlink()
    print(f"[OK] UniMERNet 模型已解压到: {dest_dir}")


if __name__ == "__main__":
    yolo_path, cfg_path = check_and_download_models()
    print(f"YOLO 模型路径: {yolo_path}")
    print(f"配置文件路径: {cfg_path}")