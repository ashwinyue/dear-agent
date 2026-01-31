# 状态定义模式

## MessagesState

```python
from langgraph.graph import MessagesState

class ChatState(MessagesState):
    """聊天状态 - 继承 LangGraph MessagesState"""
    user_id: str | None = None
    session_id: str = ""
    tenant_id: int | None = None
    iteration_count: int = 0
    max_iterations: int = 10
    error: str | None = None
```

## 自定义状态

```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from operator import add

class AgentState(TypedDict):
    """Agent 基础状态"""
    messages: Annotated[list[BaseMessage], add]
    context: dict[str, any]
    artifacts: list[any]

class ReActState(AgentState):
    """ReAct Agent 状态"""
    reasoning: str
    action: str | None
    action_input: dict[str, any]
    observation: str | None
```

## 状态验证

```python
from pydantic import BaseModel, Field

class ChatState(BaseModel):
    """带验证的状态"""
    user_id: str | None = Field(default=None, max_length=64)
    session_id: str = Field(min_length=1, max_length=128)
    iteration_count: int = Field(default=0, ge=0, le=10)

    class Config:
        extra = "ignore"
```
