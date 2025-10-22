"""
Test script to check DocLayout-YOLO model classes
"""
import sys
sys.path.insert(0, '.')

from doclayout_yolo import YOLOv10

# Load model
model = YOLOv10('weights/doclayout_yolo_docstructbench_imgsz1024.pt')

print("DocLayout-YOLO Model Classes:")
print("=" * 50)
for idx, name in model.names.items():
    print(f"  {idx}: {name}")
print("=" * 50)
