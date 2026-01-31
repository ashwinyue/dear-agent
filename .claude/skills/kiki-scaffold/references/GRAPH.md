# 图构建模式

## StateGraph

```python
from langgraph.graph import StateGraph, START, END

def build_chat_graph() -> StateGraph:
    builder = StateGraph(ChatState)

    # 添加节点
    builder.add_node("chat", chat_node)
    builder.add_node("tools", tools_node)

    # 边：START -> chat
    builder.add_edge(START, "chat")

    # 条件边
    builder.add_conditional_edges(
        "chat",
        route_by_tools,
        {
            "tools": "tools",
            "__end__": END,
        }
    )

    # 边：tools -> chat
    builder.add_edge("tools", "chat")

    return builder
```

## Command 模式

```python
from langgraph.types import Command
from typing import Literal

async def chat_node(state: ChatState, config) -> Command[Literal["tools", "__end__"]]:
    """返回 Command 进行状态更新和路由"""
    response = await llm.ainvoke(state["messages"])

    return Command(
        update={"messages": [response]},
        next=route_by_tools({"messages": state["messages"] + [response]}),
    )
```

## Checkpoint 持久化

```python
from langgraph.checkpoint import MemorySaver

async def compile_graph(builder: StateGraph) -> CompiledStateGraph:
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

# PostgreSQL Checkpointer (生产环境)
from langgraph.checkpoint.postgres import PostgresSaver

async def get_postgres_checkpointer():
    return PostgresSaver.from_conn_string(settings.database_url)
```

## 编译选项

```python
# Human-in-the-Loop
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"],  # 在执行工具前中断
)

# 中断并恢复
await graph.ainvoke(input_state, config=config)
await graph.ainvoke(Command(resume={"approved": True}), config=config)
```
