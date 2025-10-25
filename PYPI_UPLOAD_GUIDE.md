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

---

## 📤 模型文件托管方案

由于 UniMERNet 模型 1.6GB 太大，无法包含在 PyPI 包中，需要选择以下方案之一：

### 方案 1: GitHub Releases（推荐）

1. **创建 GitHub Release**

```bash
# Tag 版本
git tag v1.0.0
git push origin v1.0.0
```

2. **上传模型文件到 Release**

在 GitHub 仓库页面：
- 点击 "Releases" → "Create a new release"
- 选择 tag `v1.0.0`
- 上传 `unimernet_small.zip`（压缩后上传）
- 发布 Release

3. **修改 `model_downloader.py`**

```python
def download_unimernet_model(dest_dir):
    url = "https://github.com/yourusername/FreeP2W/releases/download/v1.0.0/unimernet_small.zip"
    zip_path = dest_dir.parent / "unimernet_small.zip"
    download_file(url, zip_path, "下载 UniMERNet 模型")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir.parent)

    zip_path.unlink()
```

### 方案 2: Hugging Face（推荐用于 AI 模型）

```python
from huggingface_hub import hf_hub_download

def download_unimernet_model(dest_dir):
    hf_hub_download(
        repo_id="yourusername/unimernet_small",
        filename="model.safetensors",
        local_dir=dest_dir
    )
```

### 方案 3: 手动下载说明

在 README.md 中提供清晰的下载指引（当前方案）。

---

## 📊 发布检查清单

发布前确保：

- [ ] 修改了 `pyproject.toml` 中的作者信息
- [ ] 修改了 GitHub 仓库链接
- [ ] 更新了 `LICENSE` 文件
- [ ] 检查了包名在 PyPI 上的可用性
- [ ] 本地测试安装成功 (`pip install -e .`)
- [ ] 构建成功 (`python -m build`)
- [ ] 包检查通过 (`twine check dist/*`)
- [ ] 在 TestPyPI 测试通过
- [ ] README.md 内容完整
- [ ] 模型文件托管方案已确定

---

## 🔄 版本更新流程

发布新版本时：

1. **更新版本号**

编辑 `pyproject.toml`:
```toml
version = "1.0.1"  # 或 1.1.0, 2.0.0
```

2. **清理和重建**

```bash
rm -rf build/ dist/ *.egg-info
python -m build
```

3. **上传新版本**

```bash
twine upload dist/*
```

---

## 📝 版本号规范

遵循语义化版本（Semantic Versioning）：

- `1.0.0` → `1.0.1`: 修复 bug
- `1.0.0` → `1.1.0`: 新增功能（向后兼容）
- `1.0.0` → `2.0.0`: 破坏性更改���不向后兼容）

---

## 🐛 常见问题

### 问题 1: 包名已被占用

**错误**: `The name 'freep2w' is already in use.`

**解决**: 修改 `pyproject.toml` 中的包名。

### 问题 2: 上传失败 - 文件太大

**错误**: `File too large. Limit is 100MB.`

**解决**: 检查是否包含了大文件（如 UniMERNet 模型）。确保 `MANIFEST.in` 排除了大文件。

### 问题 3: 权限错误

**错误**: `Invalid or non-existent authentication information.`

**解决**:
1. 检查 PyPI 用户名和密码
2. 使用 API Token 代替密码
3. 确保 `.pypirc` 配置正确

### 问题 4: 依赖冲突

**警告**: `Dependency 'torch>=2.6.0' conflicts...`

**解决**: 放宽依赖版本要求，使用 `>=` 而非 `==`。

---

## 🎉 发布成功后

1. **验证包页面**

访问: https://pypi.org/project/freep2w/

2. **测试安装**

```bash
pip install freep2w
freep2w --version
```

3. **推广项目**

- 在 GitHub 添加 PyPI 徽章
- 分享到社交媒体
- 更新项目文档

---

## 📚 参考资���

- [Python 打包用户指南](https://packaging.python.org/)
- [PyPI 官方文档](https://pypi.org/help/)
- [Twine 文档](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

---

**祝您发布顺利！** 🚀
