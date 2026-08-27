"""
    未指定Reducer时 : 使用覆盖更新的默认策略(类比git操作的merge)

    Reducer常用函数有以下几种：(Reducer 是 State 字段级别的更新合并规则。)
        默认行为：未指定Reducer时使用覆盖更新
        内置reducer函数：例如langgraph.graph.messages当中的add_messages函数
        自定义Reducer：支持用户自定义合并逻辑

    ASK AI:为什么需要 Reducer？
    AI ANSWER: 当多个节点都更新同一个 State 字段时，LangGraph 需要知道如何处理这些更新。

    ASK AI: 代码中 Reducer的默认行为 体现在哪里？
    AI ANSWER: foo 和 bar 都没有指定 Reducer，所以使用 LangGraph 的默认行为：
    invoke传入{"foo":1,"bar":["Hi"]} 经过节点1,2被 {'foo': 2, 'bar': ['Hello']}覆盖了，而不是追加。
"""
from typing import TypedDict, List
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 总状态约束
class MyState(TypedDict):
    foo : int
    bar : List[str]

# 节点函数必须有state参数
# 节点1
def node_one(state: MyState):
    return {"foo" : 2}

# 节点2
def node_two(state: MyState):
    return {"bar": ["Hello"]}

# 创建一个画布对象
graph = StateGraph(state_schema=MyState)

# 添加节点
# 给节点起别名 : 第一个参数是节点别名，第二个参数是节点函数
graph.add_node('1',node_one)
graph.add_node('2',node_two)

# 连接边
graph.add_edge(START,'1')
graph.add_edge('1','2')
graph.add_edge('2',END)

# 编译graph对象
compiled_graph = graph.compile()

# 执行已经编译的graph对象
result = compiled_graph.invoke(
    {
        "foo":1,
        "bar":["Hi"]
    }
)

print(result)
# {'foo': 2, 'bar': ['Hello']}
# 原因:节点通过invoke 传入 {"foo":1,"bar":["Hi"]} 这组数据 , 经过节点1,节点2, 被覆盖