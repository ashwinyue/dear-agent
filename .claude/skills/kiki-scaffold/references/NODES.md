# 节点函数模式

## 聊天节点

```python
from langgraph.types import Command, RunnableConfig
from typing import Literal

async def chat_node(
    state: ChatState,
    config: RunnableConfig,
) -> Command[Literal["tools", "__end__"]]:
    """聊天节点 - 调用 LLM 生成回复"""
    llm = get_llm(config)

    response = await llm.ainvoke(state["messages"])

    return Command(
        update={"messages": [response]},
        next=route_by_tools(state),
    )
```

## 工具节点

```python
async def tools_node(
    state: ChatState,
    config: RunnableConfig,
) -> Command[Literal["chat"]]:
    """工具节点 - 执行工具调用"""
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    results = []
    for tool_call in tool_calls:
        result = await execute_tool(tool_call)
        results.append(result)

    return Command(
        update={"messages": results},
        next="chat",
    )
```

## 路由函数

```python
from typing import Literal

def route_by_tools(state: ChatState) -> Literal["tools", "__end__"]:
    """根据是否有工具调用决定路由"""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "__end__"
```

## 工具执行

```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """计算表达式"""
    return str(eval(expression))

async def execute_tool(tool_call) -> BaseMessage:
    """执行工具调用"""
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    if tool_name == "calculator":
        result = calculator.invoke(tool_args)
    else:
        result = f"Unknown tool: {tool_name}"

    return ToolMessage(
        content=str(result),
        tool_call_id=tool_call["id"],
        name=tool_name,
    )
```
