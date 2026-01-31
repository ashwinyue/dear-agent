---
name: kiki-scaffold
description: Kiki 企业级 LangGraph Agent 脚手架 - 快速创建生产就绪的 Agent 应用。包含：StateGraph 图构建、Command 模式、Checkpoint 持久化、工具注册、流式输出、LLM 服务抽象。使用场景：(1) 创建新的 Agent (2) 添加工具 (3) 实现 Human-in-the-Loop (4) 配置流式响应
---

# Kiki Agent Scaffold

企业级 LangGraph Agent 开发脚手架，快速创建生产就绪的 Agent 应用。

## 核心组件

| 组件 | 文件 | 说明 |
|------|------|------|
| **状态定义** | `references/STATE.md` | ChatState、MessagesState、自定义状态 |
| **图构建** | `references/GRAPH.md` | StateGraph、条件边、Command 模式 |
| **节点函数** | `references/NODES.md` | chat_node、tools_node、路由函数 |
| **工具系统** | `references/TOOLS.md` | 工具注册表、内置工具、MCP 集成 |
| **流式输出** | `references/STREAMING.md` | SSE 流式、增量输出 |
| **LLM 服务** | `references/LLM.md` | 多模型路由、成本追踪、重试 |
| **可观测性** | `references/OBSERVABILITY.md` | structlog、Prometheus、Langfuse |

## 快速开始

```python
# 1. 定义状态
from langgraph.graph import MessagesState

class ChatState(MessagesState):
    user_id: str | None = None
    session_id: str = ""
    iteration_count: int = 0

# 2. 构建图
from langgraph.graph import StateGraph, START

def build_graph() -> StateGraph:
    builder = StateGraph(ChatState)
    builder.add_node("chat", chat_node)
    builder.add_node("tools", tools_node)
    builder.add_edge(START, "chat")
    builder.add_conditional_edges("chat", route_by_tools, {...})
    return builder

# 3. 编译并运行
graph = builder.compile(checkpointer=checkpointer)
result = await graph.ainvoke(input_state)
```

## 项目结构

```
app/
├── agent/
│   ├── graph/
│   │   ├── types.py      # 状态定义
│   │   ├── nodes.py      # 节点函数
│   │   ├── builder.py    # 图构建
│   │   └── cache.py      # 图缓存
│   ├── tools/
│   │   ├── registry.py   # 工具注册表
│   │   ├── builtin/      # 内置工具
│   │   └── mcp.py        # MCP 集成
│   ├── memory/           # 记忆管理
│   └── streaming/        # 流式输出
├── llm/
│   ├── service.py        # LLM 服务
│   ├── registry.py       # 模型注册表
│   └── providers.py      # 多模型路由
├── config/
│   ├── settings.py       # 配置管理
│   └── dependencies.py   # 依赖注入
└── observability/
    ├── logging.py        # 结构化日志
    └── metrics.py        # Prometheus 指标
```

## 工具系统

```python
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """网络搜索工具"""
    return f"搜索结果: {query}"

# 注册到工具节点
from langgraph.prebuilt import ToolNode
tool_node = ToolNode([search_web])
```

## 流式响应

```python
async def stream_chat(graph, input_state):
    async for chunk in graph.astream(input_state, mode="messages"):
        yield chunk.content
```

## 配置

```toml
# pyproject.toml
[project]
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "langgraph>=0.3.0",
    "langchain-core>=0.3.0",
    "structlog>=25.1.0",
]
```

## 命令行工具

```bash
# 创建新 Agent 模块
python scripts/new_agent.py chat --with-tools

# 创建新工具
python scripts/new_tool.py web_search
```
