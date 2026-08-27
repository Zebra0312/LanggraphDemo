"""
    系统提供的Reducer : 如使用langgraph.graph.messages当中的add_messages函数

    节点通过invoke 传入 {"foo":1,"bar":["Hi"]} 这组数据 , 经过节点1,节点2,
    根据传入节点的state所包含的reducer约束(operator.add函数),追加列表

    Reducer常用函数有以下几种：(Reducer 是 State 字段级别的更新合并规则。)
        默认行为：未指定Reducer时使用覆盖更新
        内置reducer函数：例如langgraph.graph.messages当中的add_messages函数
        自定义Reducer：支持用户自定义合并逻辑
"""
import operator
from typing import TypedDict, List, Annotated
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 总状态约束
# 添加系统提供的各种reducer函数进行追加
# 我的代码中的 bar: List[str] 很适合使用系统提供的 operator.add 作为 Reducer，实现列表追加。
# 固定格式 用Annotated注释   bar : Annotated[List[str], operator.add]
class MyState(TypedDict):
    foo : int
    bar : Annotated[List[str], operator.add]

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