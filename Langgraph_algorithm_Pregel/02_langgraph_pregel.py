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

print(f"图对象的所有节点: {graph.nodes}")
print(f"图对象的所有通道: {graph.channels}")
# 图对象的所有通道:
#  {
# 	'aggregate': <langgraph.channels.binop.BinaryOperatorAggregate object at 0x0000022F3EAB9640>,
#  	'__start__': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40C92840>,
# 	'__pregel_tasks': <langgraph.channels.topic.Topic object at 0x0000022F40C927C0>,
#       __pregel_tasks 是 LangGraph Pregel 运行时内部的任务通道，
#       用来管理每一轮要执行的具体任务；branch:to:node_x 负责触发节点，
#       而 __pregel_tasks 负责记录和调度这些实际执行任务。它属于内部实现细节，
#       不是业务状态，通常不需要直接操作。
# 	'branch:to:node_a': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40C92600>,
# 	'branch:to:node_b': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40C93E40>,
# 	'branch:to:node_b2': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40C93F40>,
# 	'branch:to:node_c': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40CA4D80>,
# 	'branch:to:node_d': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x0000022F40CA5340>}
# 	{'aggregate': ['A', 'B', 'C', 'B2', 'D', 'D']
# }
print(f"节点node_a的订阅: {graph.nodes["node_a"].triggers}")
# 节点node_a的订阅: ['branch:to:node_a']
print(f"节点node_a的写入: {graph.nodes["node_a"].writers}")
# 节点node_a的写入:
# [
#   ChannelWrite<...,...>
#       (
#           tags=None,
#           recurse=True,
#           explode_args=False,
#           func_accepts={'config': ('N/A', <class 'inspect._empty'>)},
#           writes=
#           (
#                   ChannelWriteTupleEntry
#                   (
#                           mapper=<function CompiledStateGraph.attach_node.<locals>._get_updates at 0x0000020D65ECB2E0>,
#                           value=<object object at 0x0000020D61C4A4F0>, static=None
#                   ),
#                   ChannelWriteTupleEntry
#                   (
#                           mapper=<function _control_branch at 0x0000020D65ECA340>,
#                           value=<object object at 0x0000020D61C4A4F0>, static=[]
#                   )
#           )
#        ),
#    ChannelWrite<branch:to:node_c>
#        (
#           tags=None,
#           recurse=True,
#           explode_args=False,
#           func_accepts={'config': ('N/A', <class 'inspect._empty'>)},
#           writes=
#           (
#                    ChannelWriteEntry
#                    (
#                           channel='branch:to:node_c',
#                           value=None,
#                           skip_none=False,
#                           mapper=None
#                     ),
#            )
#         ),
#    ChannelWrite<branch:to:node_b>
#        (
#           tags=None,
#           recurse=True,
#           explode_args=False,
#           func_accepts={'config': ('N/A', <class 'inspect._empty'>)},
#           writes=
#           (
#                     ChannelWriteEntry
#                     (
#                           channel='branch:to:node_b',
#                           value=None,
#                           skip_none=False,
#                           mapper=None),
#                     )
#            )
#  ]
#       {
#           'aggregate':
#               [
#                   'A',
#                   'B',
#                   'C',
#                   'B2',
#                   'D',
#                   'D'
#               ]
#       }

