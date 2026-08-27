"""
    自定义Reducer : 用户自定义合并逻辑

    Reducer常用函数有以下几种：(Reducer 是 State 字段级别的更新合并规则。)
        默认行为：未指定Reducer时使用覆盖更新
        内置reducer函数：例如langgraph.graph.messages当中的add_messages函数
        自定义Reducer：支持用户自定义合并逻辑

    ASK AI: old_value 和new _value 这两个形参在调用函数的时候是咋知道先后的?
    AI ANSWER: old_value 和 new_value 的先后不是 Python 自动判断出来的，而是 LangGraph 按约定传参。
    result = reducer(
    current_value,  # 当前 State 中已有的值
    update_value    # 节点刚刚返回的值
    )
    old_value、new_value 只是人为起的名字。真正决定含义的是 LangGraph 调用这个函数时的传参顺序。
"""
import operator
from typing import TypedDict, List, Annotated
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 总状态约束
# 固定格式 用Annotated注释
# 客制化自己的reducer, 功能设计:简单追加,不进行查重
def my_reducer(old_value, new_value):
    return old_value + new_value

class MyState(TypedDict):
    foo : int
    bar : Annotated[List[str], my_reducer]

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
# {'foo': 2, 'bar': ['Hi', 'Hello']}