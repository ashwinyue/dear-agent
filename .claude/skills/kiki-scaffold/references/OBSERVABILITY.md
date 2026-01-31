# 可观测性模式

## structlog 配置

```python
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
log.info("agent_invoked", user_id="123", session_id="abc")
```

## 日志上下文

```python
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def bind_context(**kwargs):
    for key, value in kwargs.items():
        if key == "request_id":
            request_id_var.set(value)
        structlog.contextvars.bind_contextvars(**{key: value})

bind_context(request_id="abc-123", tenant_id=1)
log.info("tool_called")  # 自动包含 request_id 和 tenant_id
```

## Prometheus 指标

```python
from prometheus_client import Counter, Histogram

agent_requests = Counter(
    "agent_requests_total",
    "Agent 请求总数",
    ["agent_type", "status"]
)
agent_duration = Histogram(
    "agent_duration_seconds",
    "Agent 处理耗时",
    ["agent_type"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

llm_requests = Counter(
    "llm_requests_total",
    "LLM 请求总数",
    ["model", "provider"]
)
tool_calls = Counter(
    "tool_calls_total",
    "工具调用总数",
    ["tool_name", "status"]
)

@contextmanager
def track_agent(agent_type: str):
    start = time.perf_counter()
    try:
        yield
        agent_requests.labels(agent_type=agent_type, status="success").inc()
    except Exception:
        agent_requests.labels(agent_type=agent_type, status="error").inc()
        raise
    finally:
        agent_duration.labels(agent_type=agent_type).observe(time.perf_counter() - start)
```

## Langfuse 集成

```python
from langfuse.langchain import LangfuseCallbackHandler

def get_langfuse_handler():
    return LangfuseCallbackHandler(
        public_key="pk-xxx",
        secret_key="sk-xxx",
        host="https://cloud.langfuse.com",
    )

# 使用
llm = ChatOpenAI(callbacks=[get_langfuse_handler()])
```

## 指标服务器

```python
from prometheus_client import start_http_server

def start_metrics_server(port: int = 9090):
    start_http_server(port)
    log.info("metrics_server_started", port=port)
```
