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

    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r[INFO] 下载进度: {percent}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, progress_hook)
    print()  # New line after download


def check_and_download_models():
    """
    Check if models exist, download if needed
    Returns: (yolo_model_path, unimernet_cfg_path)
    """
    model_dir = get_model_dir()

    # Check YOLO model
    yolo_model = model_dir / "doclayout_yolo_docstructbench_imgsz1024.pt"
    if not yolo_model.exists():
        YOLO_MODEL_URL = "https://github.com/zstar1003/FreeP2W/releases/download/v0.0.1/doclayout_yolo_docstructbench_imgsz1024.pt"
        download_file(YOLO_MODEL_URL, yolo_model, "下载 YOLO 模型")

    # Check UniMERNet model
    unimernet_dir = model_dir / "unimernet_small"
    if not unimernet_dir.exists():
        download_unimernet_model(unimernet_dir)

    # Check config file
    demo_yaml = model_dir / "demo.yaml"
    if not demo_yaml.exists():
        # Copy default config
        default_yaml = Path(__file__).parent / "demo.yaml"
        if default_yaml.exists():
            shutil.copy(default_yaml, demo_yaml)

    return str(yolo_model), str(demo_yaml)


def download_unimernet_model(dest_dir):
    print("[INFO] 自动下载 UniMERNet 模型...")
    url = "https://github.com/zstar1003/FreeP2W/releases/download/v0.0.1/unimernet_small.zip"
    zip_path = dest_dir.parent / "unimernet_small.zip"
    download_file(url, zip_path, "下载 UniMERNet 模型")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir.parent)
    
    zip_path.unlink()


if __name__ == "__main__":
    yolo_path, cfg_path = check_and_download_models()
    print(f"YOLO 模型路径: {yolo_path}")
    print(f"配置文件路径: {cfg_path}")