# DocLayout-YOLO Integration Issues and Solutions

## 问题诊断

### 当前环境问题

在尝试集成DocLayout-YOLO时发现以下问题：

1. **cv2循环导入错误**:
```
AttributeError: partially initialized module 'cv2' has no attribute 'gapi_wip_gst_GStreamerPipeline'
```

2. **fitz包冲突**:
```
RuntimeError: Directory 'static/' does not exist
```
- 系统中安装了错误的`fitz`包（不是PyMuPDF的fitz）
- 导致`import fitz`无法正常工作

### 问题原因

- 您的demo.py依赖`cv2`，但cv2在当前环境中有初始化问题
- pdf2docx使用`import fitz`（PyMuPDF），但系统中有另一个fitz包冲突

## 解决方案

### 方案1：修复环境（推荐）

```bash
# 1. 卸载冲突的fitz包
pip uninstall fitz

# 2. 确保安装了正确的PyMuPDF
pip install PyMuPDF

# 3. 重新安装cv2
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python

# 4. 测试
python demo.py --image-path test_files/test_img.png
```

### 方案2：使用subprocess调用demo.py

如果环境修复困难，可以通过subprocess分离运行：

```python
import subprocess
import json
import os

def run_doclayout_detection(image_path, model_path, output_dir="outputs"):
    """
    通过subprocess运行demo.py，避免导入冲突
    """
    cmd = [
        "python", "demo.py",
        "--image-path", image_path,
        "--model", model_path,
        "--res-path", output_dir
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    # 解析YOLO结果（需要修改demo.py输出JSON）
    return parse_yolo_results(output_dir)
```

### 方案3：直接使用doclayout_yolo库（最简单）

创建一个独立的检测脚本，不依赖cv2：

```python
# detect_layout.py

import os
import torch
from doclayout_yolo import YOLOv10
from PIL import Image


def detect_pdf_layout(pdf_path, page_num, model_path):
    """
    检测PDF页面布局，返回figure区域

    Args:
        pdf_path: PDF文件路径
        page_num: 页码（0-indexed）
        model_path: YOLO模型路径

    Returns:
        list: figure区域列表 [{'bbox': [x1,y1,x2,y2], 'type': 'figure', 'conf': 0.xx}, ...]
    """
    # 1. 使用PyMuPDF转换PDF页面为图像
    try:
        import fitz
    except:
        # 如果fitz有问题，使用pdf2image
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        img = images[0]
        img_path = f"_temp_page_{page_num}.png"
        img.save(img_path)
    else:
        pdf = fitz.open(pdf_path)
        page = pdf[page_num]
        pix = page.get_pixmap(dpi=150)
        img_path = f"_temp_page_{page_num}.png"
        pix.save(img_path)
        pdf.close()

    # 2. 运行YOLO检测
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLOv10(model_path)

    results = model.predict(
        img_path,
        imgsz=1024,
        conf=0.25,
        device=device
    )

    # 3. 解析结果
    regions = []
    if len(results) > 0 and hasattr(results[0], 'boxes'):
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cls_id = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())
            class_name = model.names[cls_id]

            regions.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'type': class_name,
                'confidence': conf
            })

    # 4. 清理临时文件
    if os.path.exists(img_path):
        os.remove(img_path)

    return regions


# 测试
if __name__ == "__main__":
    model_path = "weights/doclayout_yolo_docstructbench_imgsz1024.pt"
    pdf_path = "test_files/2503.20314v2.pdf"

    # 检测第3页
    regions = detect_pdf_layout(pdf_path, 2, model_path)

    print(f"Detected {len(regions)} regions:")
    for r in regions:
        print(f"  - {r['type']}: conf={r['confidence']:.2f}, bbox={r['bbox']}")
```

### 方案4：使用已有的ImageMerger（最实用）

考虑到环境问题，**建议继续使用之前测试成功的ImageMerger方案**：

✅ 优点：
- 已经测试成功（31张图合并成1张）
- 不依赖额外的AI模型
- 不受环境问题影响
- 速度快

运行方式：
```bash
python test_smart_merge.py
```

## 下一步建议

### 立即可行的方案

1. **检查demo.py是否能在你的环境运行**
   ```bash
   python demo.py --image-path test_files/test_img.png
   ```
   - 如果能运行 → 说明我这边环境有问题，可以继续集成
   - 如果不能运行 → 需要先修复环境

2. **如果demo.py能运行**
   - 我可以创建方案2（subprocess调用）
   - 或者创建方案3（独立检测脚本）

3. **如果demo.py不能运行**
   - 先修复环境（方案1）
   - 或者使用ImageMerger方案（已验证可用）

## 请告诉我

1. **demo.py在你的环境中能正常运行吗？**
   ```bash
   python demo.py --image-path test_files/test_img.png
   ```

2. **你希望使用哪个方案？**
   - 方案1：修复环境后继续集成DocLayout-YOLO
   - 方案2：使用subprocess调用
   - 方案3：独立检测脚本
   - 方案4：使用ImageMerger（已验证）

3. **是否有GPU可用？**
   - DocLayout-YOLO在GPU上会快很多
   - CPU也可以运行，但会慢一些

请告诉我你的选择，我会相应调整实现方案！
