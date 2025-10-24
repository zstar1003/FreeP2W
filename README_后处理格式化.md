# 后处理格式化 - 快速使用指南

## 🎯 功能

在 PDF 转 DOCX 后，自动统一英文正文格式：
- ✅ 字体：Times New Roman
- ✅ 大小：10pt
- ✅ 对齐：两端对齐

同时智能保留：
- ✅ 标题格式
- ✅ 图表标题
- ✅ 数学公式
- ✅ 目录

## 🚀 快速开始

### 如果还没有转换 PDF：

```bash
python convert_and_format.py test_files/2503.20314v2.pdf result_final.docx
```

### 如果已有 result.docx：

```bash
python post_format_english_body.py
```

输出：`result_formatted.docx`

## 📊 查看效果

```bash
python test_formatting_effect.py
```

会显示格式化前后的对比数据。

## ⚙️ 修改配置

编辑 `post_format_english_body.py` 底部：

```python
format_english_body_text(
    input_path="result.docx",
    output_path="result_formatted.docx",
    target_font='Times New Roman',  # 修改字体
    target_size=10.0,                # 修改大小
    target_alignment=WD_ALIGN_PARAGRAPH.JUSTIFY  # 修改对齐
)
```

**常用字体：**
- `'Times New Roman'` - 经典学术字体（默认）
- `'Arial'` - 无衬线字体
- `'Calibri'` - Office 默认
- `'Georgia'` - 易读字体

**常用大小：**
- `10.0` - 标准正文（默认）
- `11.0` - 较大正文
- `12.0` - 大号正文

## 📁 主要文件

| 文件 | 说明 |
|------|------|
| `post_format_english_body.py` | 核心格式化脚本 |
| `convert_and_format.py` | 一键完整流程（转换+格式化） |
| `test_formatting_effect.py` | 效果验证脚本 |
| `后处理格式化_使用指南.md` | 详细文档 |
| `后处理格式化_完成总结.md` | 完整总结 |

## 📈 测试效果

从实际测试来看：
- ✅ Times New Roman 占比：**81.6%**
- ✅ 10pt 字体占比：**84.7%**
- ✅ 保留数学字体：CMR10, CMMI10

## 💡 核心优势

**相比直接修改转换器：**
- ✅ 不改变核心代码
- ✅ 灵活调整参数
- ✅ 快速测试迭代
- ✅ 不影响公式

**相比手动调整：**
- ✅ 自动化处理
- ✅ 格式一致
- ✅ 智能识别
- ✅ 可重复使用

## 🔧 常见问题

**Q: 某些段落没被格式化？**
A: 可能被识别为标题、图表或公式。运行脚本查看"跳过的段落"统计。

**Q: 想格式化中文段落？**
A: 在代码中移除 `contains_english` 检查。

**Q: 只想改对齐方式？**
A: 注释掉字体修改部分，只保留对齐设置。

## 📚 详细文档

查看完整说明：
```bash
cat 后处理格式化_使用指南.md
cat 后处理格式化_完成总结.md
```

---

**开始使用：**
```bash
python post_format_english_body.py
```

**验证效果：**
```bash
python test_formatting_effect.py
```
