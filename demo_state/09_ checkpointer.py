"""
    LangGraph使用检查点实现长期记忆
    "pip install langgraph-checkpoint-sqlite"
    # 创建Sqlite的链接对象
    conn = sqlite3.connect('./checkpointer.db', check_same_thread=False)
    # 创建检查点
    checkpointer = SqliteSaver(conn)
    # 编译图对象 (传入检查点对象)
    compiled_graph = graph.compile(checkpointer=checkpointer)
    # 第一次调用
    result = compiled_graph.invoke(
        {},
        config=config
    )
    # 第二次调用，注意：不能传输具体的初始状态，只能传输None才可以短点续传
    result = compiled_graph.invoke(
        None,
        config=config
    )
"""
import sqlite3
from typing import TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 创建Sqlite的链接对象
conn = sqlite3.connect('./checkpointer.db', check_same_thread=False)

# 创建检查点
checkpointer = SqliteSaver(conn)

# 创建状态类
class MyState(TypedDict):
    key1 : str
    key2 : str
    key3 : str

# 创建节点
def node1(state: MyState):
    print(f"node1节点:{state}")
    return {"key1": "value1"}

# 第一次模拟异常
# def node2(state: MyState):
#     raise Exception("模拟故障")
# 第二次节点正常
def node2(state: MyState):
    print(f"node2节点:{state}")
    return {"key2": "value2"}

def node3(state: MyState):
    print(f"node3节点:{state}")
    return {"key3": "value3"}

# 构建图对象
graph = StateGraph(state_schema=MyState)

# 添加节点
graph.add_node(node1)
graph.add_node(node2)
graph.add_node(node3)

# 添加边
graph.add_edge(START, "node1")
graph.add_edge("node1", "node2")
graph.add_edge("node2", "node3")
graph.add_edge("node3", END)

# 编译图对象 (传入检查点对象)
compiled_graph = graph.compile(checkpointer=checkpointer)

# 执行图对象
config = {
    "configurable":{
        "thread_id":"abc"
    }
}

# 第一次调用
# result = compiled_graph.invoke(
#     {},
#     config=config
# )
# 第二次调用，注意：不能传输具体的初始状态，只能传输None才可以短点续传
result = compiled_graph.invoke(
    None,
    config=config
)


print(result)