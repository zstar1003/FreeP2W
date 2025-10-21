"""
PDF 图片分布分析工具

用于诊断 PDF 中图片是否被切割成多个小块（tiling）
"""

import fitz
from collections import defaultdict


def analyze_pdf_images(pdf_path):
    """分析 PDF 中的图片分布，检测是否有图片切割问题"""

    print("=" * 80)
    print(f"分析 PDF 文件: {pdf_path}")
    print("=" * 80)

    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        print(f"\n{'='*80}")
        print(f"第 {page_num + 1} 页")
        print(f"{'='*80}")
        print(f"检测到图片数量: {len(images)}")

        if not images:
            print("  [!] This page has no embedded bitmap images")
            continue

        # 收集所有图片的位置信息
        all_rects = []
        for i, img in enumerate(images):
            rects = page.get_image_rects(img)
            for rect in rects:
                all_rects.append({
                    'id': i,
                    'rect': rect,
                    'width': rect.width,
                    'height': rect.height,
                    'area': rect.width * rect.height,
                    'x0': rect.x0,
                    'y0': rect.y0,
                    'x1': rect.x1,
                    'y1': rect.y1
                })

        # 按位置排序
        all_rects.sort(key=lambda x: (x['y0'], x['x0']))

        # 输出图片详情
        print(f"\n图片详细信息:")
        for i, rect_info in enumerate(all_rects):
            print(f"  [{i+1}] 尺寸: {rect_info['width']:.1f} x {rect_info['height']:.1f} pt | "
                  f"面积: {rect_info['area']:.0f} pt² | "
                  f"位置: ({rect_info['x0']:.1f}, {rect_info['y0']:.1f})")

        # 检测潜在的切割问题
        print(f"\n问题诊断:")

        # 1. 检测小图片块
        small_images = [r for r in all_rects if r['width'] < 50 or r['height'] < 50]
        if len(small_images) > 10:
            print(f"  ⚠️  检测到大量小图片块: {len(small_images)} 个")
            print(f"     这可能是大图被切割的症状！")

        # 2. 检测网格状排列
        if len(all_rects) >= 4:
            # 提取 y 坐标和 x 坐标
            y_coords = sorted(set(r['y0'] for r in all_rects))
            x_coords = sorted(set(r['x0'] for r in all_rects))

            if len(y_coords) >= 2 and len(x_coords) >= 2:
                # 检查间距是否规则
                y_gaps = [y_coords[i+1] - y_coords[i] for i in range(len(y_coords)-1)]
                x_gaps = [x_coords[i+1] - x_coords[i] for i in range(len(x_coords)-1)]

                avg_y_gap = sum(y_gaps) / len(y_gaps) if y_gaps else 0
                avg_x_gap = sum(x_gaps) / len(x_gaps) if x_gaps else 0

                y_regular = all(abs(gap - avg_y_gap) < 5 for gap in y_gaps) if y_gaps else False
                x_regular = all(abs(gap - avg_x_gap) < 5 for gap in x_gaps) if x_gaps else False

                if y_regular and x_regular:
                    print(f"  ⚠️  检测到网格状图片排列!")
                    print(f"     行数: {len(y_coords)}, 列数: {len(x_coords)}")
                    print(f"     总共: {len(y_coords)} x {len(x_coords)} = {len(y_coords) * len(x_coords)} 个图片块")
                    print(f"     这很可能是一张大图被切割成了网格!")

        # 3. 检测相邻的图片
        adjacent_pairs = 0
        gap_threshold = 5.0  # 5 pt

        for i in range(len(all_rects)):
            for j in range(i + 1, len(all_rects)):
                r1, r2 = all_rects[i], all_rects[j]

                # 检查是否水平相邻
                if abs(r1['y0'] - r2['y0']) < gap_threshold:
                    if abs(r1['x1'] - r2['x0']) < gap_threshold or abs(r2['x1'] - r1['x0']) < gap_threshold:
                        adjacent_pairs += 1

                # 检查是否垂直相邻
                if abs(r1['x0'] - r2['x0']) < gap_threshold:
                    if abs(r1['y1'] - r2['y0']) < gap_threshold or abs(r2['y1'] - r1['y0']) < gap_threshold:
                        adjacent_pairs += 1

        if adjacent_pairs > 0:
            print(f"  ⚠️  检测到 {adjacent_pairs} 对相邻图片")
            print(f"     这些图片可能需要合并!")

        # 4. 计算页面覆盖率
        page_area = page.rect.width * page.rect.height
        total_image_area = sum(r['area'] for r in all_rects)
        coverage = (total_image_area / page_area) * 100

        print(f"\n图片覆盖率: {coverage:.1f}%")
        if coverage > 80:
            print(f"  ℹ️  图片覆盖了大部分页面，可能是整页图片")

        # 5. 检测是否有矢量图形（drawings）
        drawings = page.get_drawings()
        if drawings:
            print(f"\n矢量图形: 检测到 {len(drawings)} 个绘制元素")
            print(f"  ℹ️  页面同时包含矢量图形和位图")

    doc.close()

    print(f"\n{'='*80}")
    print("分析完成")
    print("=" * 80)


def main():
    pdf_file = 'test_files/2503.20314v2.pdf'

    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + " " * 20 + "PDF 图片切割问题诊断工具" + " " * 20 + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    print("\n")

    try:
        analyze_pdf_images(pdf_file)

        print("\n")
        print("诊断结果说明:")
        print("-" * 80)
        print("如果出现以下情况，说明存在图片切割问题:")
        print("  1. 大量小图片块 (< 50pt)")
        print("  2. 网格状图片排列")
        print("  3. 大量相邻图片对")
        print()
        print("解决方案:")
        print("  - 如果是网格状: 使用图片拼接算法合并")
        print("  - 如果是不规则: 使用 OpenCV Stitcher")
        print("  - 如果图片很大: 增大合并的间隙阈值")
        print("-" * 80)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
