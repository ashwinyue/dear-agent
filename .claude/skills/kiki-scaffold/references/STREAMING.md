# 流式输出模式

## SSE 流式

```python
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

async def chat_stream(request: ChatRequest):
    async def event_generator():
        async for chunk, metadata in agent.astream(
            input={"messages": request.messages},
        ):
            yield {
                "event": "token",
                "data": {
                    "content": chunk.content,
                    "type": chunk.type,
                },
            }
        yield {"event": "done", "data": {"done": True}}

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

## LangGraph 流式

```python
async def stream_chat(graph, input_state):
    """流式调用 - messages 模式"""
    async for chunk in graph.astream(
        input_state,
        mode="messages",
    ):
        # chunk 是增量消息
        yield chunk.content

async def stream_updates(graph, input_state):
    """流式调用 - updates 模式"""
    async for update in graph.astream(
        input_state,
        mode="updates",
    ):
        # update 是状态更新
        yield update

async def stream_values(graph, input_state):
    """流式调用 - values 模式"""
    async for value in graph.astream(
        input_state,
        mode="values",
    ):
        # value 是完整状态
        yield value["messages"][-1]
```

## 自定义流式

```python
from app.agent.streaming.base import BaseStreamingHandler

class ChatStreamingHandler(BaseStreamingHandler):
    async def handle_chunk(self, chunk: any) -> str:
        """处理消息块"""
        return chunk.content

    async def handle_end(self) -> str:
        """流结束处理"""
        return "[DONE]"
```

## 流式配置

```python
# 在图中配置
from langgraph.types import StreamMode

graph = builder.compile(
    checkpointer=checkpointer,
    stream_mode=["messages", "updates"],
)
```
