"""
    获取历史状态

    注意：获取历史状态，必须结合记忆使用（checkpointer）
    # 获取最近的一次历史状态
    print(graph.get_state(config=config))
    # 获取所有的历史状态
    all_history = graph.get_state_history(config=config)
    for history in all_history:
        print(history)

    | 字段名称 | 类型 | 含义说明 |
    |:---:|:---|:---|
    | **values** | `dict[str, Any] \| Any` | 当前状态快照中保存的状态数据，例如对话内容、业务字段等。 |
    | **next** | `tuple[str, ...]` | 当前超步执行完成后，下一步准备执行的节点名称。为空元组 `()` 时，表示没有后续节点，图执行结束。 |
    | **config** | `RunnableConfig` | 获取或定位当前状态快照所需的配置信息，通常包括 `thread_id`、`checkpoint_id` 等。 |
    | **metadata** | `CheckpointMetadata` | 当前状态快照的附加元数据，例如执行步骤、快照来源、节点更新信息等。 |
    | **parent_config** | `RunnableConfig` | 父级状态快照对应的配置，可用于沿着检查点链回溯上一个状态。没有父快照时通常为空。 |
    | **interrupts** | `tuple[Interrupt, ...]` | 当前超步中产生但尚未处理的中断信息，用于暂停和恢复图的执行。 |
"""

import operator
from typing import TypedDict, Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

class MyState(TypedDict):
    aggregate : Annotated[list[str], operator.add]

def node_a(state: MyState):
    return {"aggregate": ["A"]}
def node_b(state: MyState):
    return {"aggregate": ["B"]}
def node_b2(state: MyState):
    return {"aggregate": ["B2"]}
def node_c(state: MyState):
    return {"aggregate": ["C"]}
def node_d(state: MyState):
    return {"aggregate": ["D"]}

builder = StateGraph(state_schema=MyState)

builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_b2)
builder.add_node(node_c)
builder.add_node(node_d)

# START → a → b、c → b_2、d → d → END
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_a", "node_c")
builder.add_edge("node_b", "node_b2")
builder.add_edge("node_c", "node_d")
builder.add_edge("node_b2", "node_d")
builder.add_edge("node_d", END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer = checkpointer)

config = {
    "configurable":{
        "thread_id" : "abc"
    }
}

result = graph.invoke({},config)
print(result)

# 分隔符
print("="*200)

# 获取最近的一次历史状态
print(graph.get_state(config=config))
print("="*200)

# 获取所有的历史状态
all_history = graph.get_state_history(config=config)
print(all_history)
# <generator object Pregel.get_state_history at 0x0000020FB7DECE00> 该方法返回的是一个生成器 需要遍历取值
for history in all_history:
    print(history)
