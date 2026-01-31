# 工具系统模式

## 工具定义

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="搜索查询")
    limit: int = Field(default=5, ge=1, le=20)

@tool
def web_search(input: SearchInput) -> str:
    """网络搜索工具"""
    # 实现搜索逻辑
    return f"结果: {input.query}"

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 天气: 晴朗"
```

## 工具注册表

```python
from typing import List, Dict, Any

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Any] = {}

    def register(self, tool: Any) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Any:
        return self._tools.get(name)

    def list_tools(self) -> List[Any]:
        return list(self._tools.values())

    def list_available(self) -> List[Dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]
```

## ToolNode 集成

```python
from langgraph.prebuilt import ToolNode

# 创建工具节点
tool_node = ToolNode([web_search, get_weather])

# 在图中使用
builder.add_node("tools", tool_node)
```

## MCP 工具

```python
from mcp_client import MCPClient

class MCPToolAdapter:
    def __init__(self, client: MCPClient):
        self.client = client

    def as_langchain_tool(self, mcp_tool):
        @tool
        def wrapper(**kwargs):
            return self.client.call_tool(mcp_tool.name, kwargs)
        wrapper.name = mcp_tool.name
        wrapper.description = mcp_tool.description
        return wrapper
```

## 工具拦截器

```python
class ToolInterceptor:
    async def before_execute(self, tool_name: str, args: dict) -> dict:
        """前置拦截 - 参数验证、日志"""
        log.info("tool_execute", tool=tool_name, args=kwargs)
        return args

    async def after_execute(self, tool_name: str, result: any) -> any:
        """后置拦截 - 结果处理、错误转换"""
        return result
```
