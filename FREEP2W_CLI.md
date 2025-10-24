# FreeP2W - 命令行工具使用指南

## 🚀 快速开始

### 方法1：直接使用 Python（推荐）

```bash
python freep2w.py input.pdf
```

### 方法2：使用批处理文件（Windows）

```bash
freep2w.bat input.pdf
```

### 方法3：打包为 exe（可选）

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
build_exe.bat

# 使用
dist\freep2w\freep2w.exe input.pdf
```

---

## 📖 命令行选项

### 基本用法

```bash
freep2w input.pdf                    # 输出为 input_converted.docx
```

### 指定输出文件

```bash
freep2w input.pdf -o output.docx     # 指定输出文件名
```

### 完整示例

```bash
freep2w test_files/2503.20314v2.pdf -o result_final.docx
```

---

## 🎯 输出说明

### 简洁模式输出

程序只显示关键信息：

```
[INFO] 正在加载转换器...
[INFO] 开始转换 PDF...
[INFO] PDF 转换完成
[INFO] 开始格式化文档...
[INFO] 格式化完成
[保存] 已保存到: output.docx
```

### 隐藏的处理步骤

以下步骤在后台自动完成（不显示输出）：
- YOLO 模型加载
- 图片和公式检测
- UniMERNet 公式识别
- pdf2docx 文本提取
- 格式化处理

---

## ⚙️ 功能特性

### 自动处理
1. **公式识别**：使用 DocLayout-YOLO + UniMERNet
2. **格式统一**：
   - 英文正文字体：Times New Roman
   - 字体大小：10pt
   - 对齐方式：两端对齐
3. **智能保留**：
   - 标题格式
   - 图表标题
   - 数学公式
   - 目录格式

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `freep2w.py` | 主程序（Python 脚本） |
| `freep2w.bat` | Windows 批处理启动器 |
| `freep2w.spec` | PyInstaller 打包配置 |
| `build_exe.bat` | 打包脚本 |

---

## 🔧 打包为 exe

### 步骤

1. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **执行打包**
   ```bash
   build_exe.bat
   ```

3. **使用 exe**
   ```bash
   dist\freep2w\freep2w.exe input.pdf
   ```

### 注意事项

- 打包后的程序较大（包含所有依赖）
- 首次运行可能需要一些时间加载模型
- 确保 `weights` 目录和 `demo.yaml` 在同一目录

---

## 💡 使用技巧

### 批量处理

创建批处理脚本：

```batch
@echo off
for %%f in (*.pdf) do (
    echo 正在处理: %%f
    python freep2w.py "%%f" -o "%%~nf_converted.docx"
)
echo 全部完成！
pause
```

### 添加到 PATH

将 FreeP2W 目录添加到系统 PATH，然后可以在任何位置调用：

```bash
freep2w C:\Documents\paper.pdf -o C:\Output\result.docx
```

---

## 🐛 故障排除

### 问题1：找不到模型文件

**错误：** `FileNotFoundError: weights/...`

**解决：** 确保当前目录有 `weights` 文件夹

### 问题2：缺少依赖

**错误：** `ModuleNotFoundError: No module named '...'`

**解决：** 安装依赖
```bash
pip install -r requirements.txt
```

### 问题3：内存不足

**错误：** `MemoryError` 或程序卡死

**解决：**
- 关闭其他程序释放内存
- 处理较小的 PDF 文件
- 考虑分页转换

---

## 📊 性能说明

### 处理速度

| PDF 页数 | 预计时间 |
|---------|---------|
| 1-10 页 | 1-2 分钟 |
| 11-50 页 | 3-10 分钟 |
| 51-100 页 | 10-20 分钟 |

*注：实际速度取决于 CPU/GPU、公式数量等因素*

### 内存占用

- 最低：4GB RAM
- 推荐：8GB+ RAM
- GPU：可选（CUDA 加速）

---

## ✅ 完整示例

```bash
# 示例 1: 基本转换
python freep2w.py paper.pdf

# 示例 2: 指定输出
python freep2w.py paper.pdf -o formatted_paper.docx

# 示例 3: 使用 bat 文件
freep2w.bat paper.pdf

# 示例 4: 使用 exe（如已打包）
freep2w.exe paper.pdf -o output.docx

# 示例 5: 显示版本
python freep2w.py --version

# 示例 6: 显示帮助
python freep2w.py --help
```

---

## 🎉 总结

**FreeP2W 命令行工具特点：**

✅ **简洁输出**：只显示关键信息
✅ **自动化**：一条命令完成转换和格式化
✅ **灵活**：支持多种使用方式
✅ **专业**：保留公式，统一格式

---

**立即使用：**
```bash
python freep2w.py your_paper.pdf -o output.docx
```
