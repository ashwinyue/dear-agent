# LLM 服务模式

## LLMService

```python
from typing import Literal

class LLMService:
    def __init__(
        self,
        default_model: str | None = None,
        max_retries: int = 3,
    ):
        self._default_model = default_model
        self._max_retries = max_retries
        self._llm: BaseChatModel | None = None

    def get_llm(
        self,
        model: str | None = None,
        temperature: float = 0.7,
    ) -> BaseChatModel:
        """获取 LLM 实例"""
        model_name = model or self._default_model
        return get_chat_model(model_name, temperature=temperature)

    def get_llm_with_tools(
        self,
        tools: list[Any] | None = None,
        model: str | None = None,
    ) -> BaseChatModel:
        """获取带工具的 LLM"""
        llm = self.get_llm(model)
        if tools:
            llm = llm.bind_tools(tools)
        return llm

    async def chat(
        self,
        messages: list[dict | BaseMessage],
        model: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """聊天接口"""
        llm = self.get_llm(model)
        response = await llm.ainvoke(messages)
        return {"content": response.content, "tool_calls": response.tool_calls}

    async def chat_stream(
        self,
        messages: list[dict | BaseMessage],
        model: str | None = None,
    ):
        """流式聊天"""
        llm = self.get_llm(model)
        async for chunk in llm.astream(messages):
            yield chunk.content
```

## 模型注册表

```python
from typing import Dict, Type

MODEL_REGISTRY: Dict[str, Type[BaseChatModel]] = {
    "gpt-4o": ChatOpenAI(model="gpt-4o"),
    "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini"),
    "claude-3-5-sonnet": ChatAnthropic(model="claude-3-5-sonnet-20241022"),
    "deepseek-chat": DeepSeekChat(model="deepseek-chat"),
    "qwen-turbo": QwenChat(model="qwen-turbo"),
}

def get_chat_model(name: str, **kwargs) -> BaseChatModel:
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {name}")
    return MODEL_REGISTRY[name](**kwargs)
```

## 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryableLLMService(LLMService):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
    )
    async def chat_with_retry(self, messages, **kwargs):
        return await self.chat(messages, **kwargs)
```

## 成本追踪

```python
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0

    def track(self, model: str, prompt_tokens: int, completion_tokens: int):
        cost_per_1k = {"gpt-4o": 0.005, "gpt-4o-mini": 0.00015}
        price = cost_per_1k.get(model, 0.01)
        cost = (prompt_tokens + completion_tokens) / 1000 * price

        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += cost
```
