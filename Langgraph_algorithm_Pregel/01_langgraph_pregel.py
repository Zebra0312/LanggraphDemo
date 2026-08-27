"""
    获取所有actors节点,channels通道,节点的订阅和写入

    StateGraph
        │
        │ compile()
        ▼
    Pregel
        ├── Actors
        │     └── PregelNode：节点
        │
        └── Channels
              ├── aggregate：状态通道
              └── branch:to:*：节点触发通道

         +-----------+
         | __start__ |
         +-----------+
                *
                *
                *
           +--------+
           | node_a |
           +--------+
          **        **
        **            **
       *                **
+--------+                *
| node_b |                *
+--------+                *
      *                   *
      *                   *
      *                   *
+---------+          +--------+
| node_b2 |          | node_c |
+---------+          +--------+
          **        **
            **    **
              *  *
           +--------+
           | node_d |
           +--------+
                *
                *
                *
          +---------+
          | __end__ |
          +---------+

"""
import operator
from typing import TypedDict, Annotated
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

graph = builder.compile()

result = graph.invoke({})
print(result)

graph_structure = graph.get_graph()
res = graph_structure.draw_ascii()
print(res)

# Plan
#   ↓
# 选择本轮激活节点
#   ↓
# Execute
#   ↓
# 并行执行节点
#   ↓
# Update
#   ↓
# 合并状态、更新 Channel
#   ↓
# 保存 Checkpoint
#   ↓
# 进入下一轮
