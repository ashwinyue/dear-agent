"""Agent 项目初始化脚本"""

import argparse
import os
from pathlib import Path


def init_agent_project(
    name: str,
    output_dir: str = ".",
):
    """初始化 Agent 项目"""
    output_path = Path(output_dir) / name
    output_path.mkdir(parents=True, exist_ok=True)

    # 创建目录结构
    structure = {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "agent": {
                "__init__.py": "",
                "graph": {
                    "__init__.py": "",
                    "types.py": "",
                    "nodes.py": "",
                    "builder.py": "",
                },
                "tools": {
                    "__init__.py": "",
                    "registry.py": "",
                    "builtin": {"__init__.py": ""},
                },
                "memory": {"__init__.py": ""},
                "streaming": {"__init__.py": ""},
            },
            "llm": {
                "__init__.py": "",
                "service.py": "",
                "registry.py": "",
            },
            "config": {
                "__init__.py": "",
                "settings.py": "",
            },
            "observability": {
                "__init__.py": "",
                "logging.py": "",
                "metrics.py": "",
            },
        },
        "tests": {
            "__init__.py": "",
            "conftest.py": "",
            "test_agent": {"__init__.py": ""},
        },
        ".claude": {"rules": {}, "skills": {}},
    }

    def create_structure(base: Path, structure: dict):
        for name, content in structure.items():
            path = base / name
            if isinstance(content, dict):
                path.mkdir(parents=True, exist_ok=True)
                create_structure(path, content)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

    create_structure(output_path, structure)

    # main.py
    main_content = f'''"""{name} - Agent 应用入口"""

from fastapi import FastAPI
from app.config.settings import get_settings
from app.observability.logging import configure_logging

settings = get_settings()
configure_logging(environment=settings.environment)

app = FastAPI(
    title="{name}",
    description="Kiki Agent Framework",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    (output_path / "app" / "main.py").write_text(main_content)

    # settings.py
    settings_content = '''"""配置管理"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False

    llm_provider: Literal["openai", "anthropic", "ollama", "deepseek", "mock"] = "mock"
    llm_model: str = "gpt-4o"

    model_config = SettingsConfigDict(
        env_prefix="kiki_",
        case_sensitive=False,
        extra="ignore",
    )

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
'''
    (output_path / "app" / "config" / "settings.py").write_text(settings_content)

    # logging.py
    logging_content = '''"""日志配置"""

import structlog

def configure_logging(environment: str = "development"):
    if environment == "production":
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.OBoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    else:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.OBoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

log = structlog.get_logger()
'''
    (output_path / "app" / "observability" / "logging.py").write_text(logging_content)

    # pyproject.toml
    pyproject_content = f'''[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.13"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "langgraph>=0.3.0",
    "langchain-core>=0.3.0",
    "langchain-openai>=0.2.0",
    "structlog>=25.1.0",
]

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = ["-v", "--tb=short"]
'''
    (output_path / "pyproject.toml").write_text(pyproject_content)

    # CLAUDE.md
    claude_content = f'''# {name}

Kiki Agent Framework 项目。

## 快速开始

```bash
uv sync
uv run uvicorn app.main:app --reload
```
'''
    (output_path / "CLAUDE.md").write_text(claude_content)

    print(f"项目 '{name}' 创建完成！")
    print(f"位置: {output_path}")
    print("\n下一步:")
    print(f"  cd {output_path}")
    print("  uv sync")


def main():
    parser = argparse.ArgumentParser(description="初始化 Agent 项目")
    parser.add_argument("name", help="项目名称")
    parser.add_argument("--output", "-o", default=".", help="输出目录")

    args = parser.parse_args()

    init_agent_project(name=args.name, output_dir=args.output)


if __name__ == "__main__":
    main()
