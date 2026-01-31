"""Agent 模块创建脚本"""

import argparse
import os
import re
from pathlib import Path
from jinja2 import Template

TEMPLATES_DIR = Path(__file__).parent / ".." / "templates"


def to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def to_pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))


def render_template(template_str: str, context: dict) -> str:
    template = Template(template_str)
    return template.render(**context)


def create_agent_module(name: str, output_dir: str = ".", with_tools: bool = True):
    """创建新的 Agent 模块"""
    snake_name = to_snake_case(name)
    pascal_name = to_pascal_case(name)

    output_path = Path(output_dir) / "agent" / snake_name
    output_path.mkdir(parents=True, exist_ok=True)

    context = {
        "name": snake_name,
        "title": pascal_name,
    }

    # 创建 types.py
    types_content = f'''"""{pascal_name} Agent 类型定义"""

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class {pascal_name}State(MessagesState):
    """{pascal_name} 状态"""
    user_id: str | None = Field(default=None, description="用户 ID")
    session_id: str = Field(default="", description="会话 ID")
    tenant_id: int | None = Field(default=None, description="租户 ID")
    iteration_count: int = Field(default=0, ge=0, le=10, description="迭代次数")
    max_iterations: int = Field(default=10, description="最大迭代次数")
    error: str | None = Field(default=None, description="错误信息")
'''
    (output_path / "types.py").write_text(types_content)

    # 创建 nodes.py
    nodes_content = f'''"""{pascal_name} Agent 节点函数"""

from typing import Literal
from langgraph.types import Command, RunnableConfig
from .{types} import {pascal_name}State


async def {snake_name}_node(
    state: {pascal_name}State,
    config: RunnableConfig,
) -> Command[Literal["tools", "__end__"]]:
    """{pascal_name} 节点 - 调用 LLM 生成回复"""
    # TODO: 实现 LLM 调用逻辑
    pass


async def tools_node(
    state: {pascal_name}State,
    config: RunnableConfig,
) -> Command[Literal["{snake_name}"]]:
    """工具节点 - 执行工具调用"""
    # TODO: 实现工具调用逻辑
    pass


def route_by_tools(state: {pascal_name}State) -> Literal["tools", "__end__"]:
    """路由函数 - 根据是否有工具调用决定路由"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"
'''
    (output_path / "nodes.py").write_text(nodes_content)

    # 创建 builder.py
    builder_content = f'''"""{pascal_name} Agent 图构建"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Checkpointer
from .{types} import {pascal_name}State
from .{nodes} import {snake_name}_node, tools_node, route_by_tools


def build_{snake_name}_graph() -> StateGraph:
    """构建 {pascal_name} Agent 图"""
    builder = StateGraph({pascal_name}State)

    # 添加节点
    builder.add_node("{snake_name}", {snake_name}_node)
    builder.add_node("tools", tools_node)

    # 边
    builder.add_edge(START, "{snake_name}")
    builder.add_conditional_edges(
        "{snake_name}",
        route_by_tools,
        {{
            "tools": "tools",
            "__end__": END,
        }}
    )
    builder.add_edge("tools", "{snake_name}")

    return builder


async def compile_{snake_name}_graph(
    builder: StateGraph,
    checkpointer: Checkpointer,
) -> "CompiledStateGraph":
    """编译 {pascal_name} Agent 图"""
    return builder.compile(checkpointer=checkpointer)
'''
    (output_path / "builder.py").write_text(builder_content)

    # 创建 __init__.py
    init_content = f'''"""{pascal_name} Agent 模块"""

from .{types} import {pascal_name}State
from .{nodes} import {snake_name}_node, tools_node, route_by_tools
from .{builder} import build_{snake_name}_graph, compile_{snake_name}_graph

__all__ = [
    "{pascal_name}State",
    "{snake_name}_node",
    "tools_node",
    "route_by_tools",
    "build_{snake_name}_graph",
    "compile_{snake_name}_graph",
]
'''
    (output_path / "__init__.py").write_text(init_content)

    print(f"Agent 模块 '{pascal_name}' 创建完成！")
    print(f"位置: {output_path}")
    return True


def create_tool(name: str, output_dir: str = "."):
    """创建新工具"""
    snake_name = to_snake_case(name)
    pascal_name = to_pascal_case(name)

    output_path = Path(output_dir) / "agent" / "tools" / "builtin"
    output_path.mkdir(parents=True, exist_ok=True)

    tool_content = f'''"""{pascal_name} 工具"""

from langchain.tools import tool
from pydantic import BaseModel, Field


class {pascal_name}Input(BaseModel):
    """{pascal_name} 输入参数"""
    query: str = Field(description="查询内容")


@tool
def {snake_name}(input: {pascal_name}Input) -> str:
    """{pascal_name} 工具"""
    # TODO: 实现工具逻辑
    return f"Result: {{input.query}}"
'''
    (output_path / f"{snake_name}.py").write_text(tool_content)

    print(f"工具 '{pascal_name}' 创建完成！")
    print(f"位置: {output_path / f'{snake_name}.py'}")
    return True


def main():
    parser = argparse.ArgumentParser(description="创建 Agent 模块或工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # Agent 模块命令
    agent_parser = subparsers.add_parser("agent", help="创建 Agent 模块")
    agent_parser.add_argument("name", help="模块名称 (PascalCase)")
    agent_parser.add_argument("--output", "-o", default=".", help="输出目录")

    # 工具命令
    tool_parser = subparsers.add_parser("tool", help="创建工具")
    tool_parser.add_argument("name", help="工具名称 (PascalCase)")
    tool_parser.add_argument("--output", "-o", default=".", help="输出目录")

    args = parser.parse_args()

    if args.command == "agent":
        create_agent_module(args.name, args.output)
    elif args.command == "tool":
        create_tool(args.name, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
