# FreeP2W - PyPI 发布指南

完整的 PyPI 发布流程指南

---

## 📋 前置准备

### 1. 注册 PyPI 账号

- **PyPI 官网**: https://pypi.org/account/register/
- **TestPyPI** (测试用): https://test.pypi.org/account/register/

### 2. 安装必要工具

```bash
pip install --upgrade build twine
```

---

## 🔧 配置步骤

### 步骤 1: 修改项目信息

编辑 `pyproject.toml` 文件，修改以下内容：

```toml
[project]
name = "freep2w"  # PyPI 包名（必须唯一）
version = "1.0.0"  # 版本号
authors = [
    {name = "您的名字", email = "your.email@example.com"}  # 修改这里
]

[project.urls]
Homepage = "https://github.com/yourusername/FreeP2W"  # 修改这里
Repository = "https://github.com/yourusername/FreeP2W"  # 修改这里
```

### 步骤 2: 修改 LICENSE

编辑 `LICENSE` 文件，替换 `Your Name` 为您的真实姓名。

### 步骤 3: 检查包名可用性

访问 https://pypi.org/project/freep2w/ 检查包名是否已被占用。

如果已被占用，修改 `pyproject.toml` 中的 `name`，例如：

- `freep2w-converter`
- `pdf2word-free`
- `freepdf2word`

---

## 📦 构建和测试

### 1. 本地测试安装

```bash
# 在项目根目录执行
python -m pip install -e .
```

测试命令是否可用：

```bash
freep2w --help
```

### 2. 构建分发包

```bash
# 清理旧的构建文件
rm -rf build/ dist/ *.egg-info

# 构建
python -m build
```

构建完成后，`dist/` 目录应包含：

- `freep2w-1.0.0-py3-none-any.whl` (wheel 包)
- `freep2w-1.0.0.tar.gz` (源码包)

### 3. 检查包

```bash
twine check dist/*
```

确保输出为：

```
Checking dist/freep2w-1.0.0-py3-none-any.whl: PASSED
Checking dist/freep2w-1.0.0.tar.gz: PASSED
```

---

## 🚀 上传到 PyPI

### 方案 A: 先上传到 TestPyPI（推荐）

1. **上传到 TestPyPI**

```bash
twine upload --repository testpypi dist/*
```

输入 TestPyPI 用户名和密码。

2. **从 TestPyPI 测试安装**

```bash
pip install --index-url https://test.pypi.org/simple/ freep2w
```

3. **测试功能**

```bash
freep2w test.pdf -o output.docx
```

### 方案 B: 直接上传到 PyPI

```bash
twine upload dist/*
```

输入 PyPI 用户名和密码。

---

## 🔑 使用 API Token（推荐）

### 1. 生成 API Token

1. 登录 PyPI: https://pypi.org/manage/account/token/
2. 点击 "Add API token"
3. 设置 token 名称和范围
4. 复制生成的 token（格式：`pypi-AgEIcHlwaS5vcmc...`）

### 2. 配置 `.pypirc`

创建或编辑 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 您的 PyPI token

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 您的 TestPyPI token
repository = https://test.pypi.org/legacy/
```

### 3. 使用 Token 上传

```bash
# 上传到 PyPI（使用 token）
twine upload dist/*

# 上传到 TestPyPI（使用 token）
twine upload --repository testpypi dist/*
```
