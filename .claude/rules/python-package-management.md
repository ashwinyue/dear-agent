# Python Package Management

## MANDATORY: Use uv Only

本项目**强制**使用 `uv` 作为唯一的 Python 包管理工具。

## 禁止行为

**NEVER** 使用以下工具：
- `pip`
- `pipenv`
- `poetry`
- `conda`
- `virtualenv` + `pip`
- 任何其他 Python 包管理器

## 标准操作

### 初始化项目
```bash
uv init
uv sync
```

### 添加依赖
```bash
# 生产依赖
uv add package-name

# 开发依赖
uv add --dev package-name

# 指定版本
uv add "package-name>=1.0.0"
uv add "package-name==1.2.3"
```

### 删除依赖
```bash
uv remove package-name
```

### 运行命令
```bash
# 使用虚拟环境中的 Python
uv run python script.py

# 使用虚拟环境中的命令
uv run ruff check .
uv run pytest

# 激活 shell（不推荐，更推荐 uv run）
uv shell
```

### 同步依赖
```bash
uv sync
uv sync --dev  # 包含开发依赖
```

### 锁文件管理
- `uv.lock` **必须** 提交到版本控制
- 修改依赖后**必须**运行 `uv lock` 更新锁文件

## Python 版本

项目使用 `uv` 管理 Python 版本：
- Python 版本定义在 `pyproject.toml` 的 `requires-python` 字段
- 使用 `uv python list` 查看可用版本
- 使用 `uv python install 3.13` 安装指定版本

## 迁移指南

如果需要迁移现有项目：
```bash
# 从 requirements.txt 迁移
uv add -r requirements.txt

# 从 setup.py/pyproject.toml 迁移
uv sync
```

## 常见问题

**Q: 如何运行测试？**
```bash
uv run pytest
```

**Q: 如何运行代码检查？**
```bash
uv run ruff check .
uv run mypy app/
```

**Q: 如何启动开发服务器？**
```bash
uv run uvicorn app.main:app --reload
```

## 违规检查

CI/CD 将检测是否有非 uv 的包管理操作：
- 检测 `pip install` 调用
- 检测 `Pipfile` / `poetry.lock` / `environment.yml` 文件
- 确认 `uv.lock` 存在且最新
