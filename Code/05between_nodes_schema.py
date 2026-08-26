"""
    节点间数据隔离

    LangGraph当中节点通过接收不同的状态，还可以为一个非全局状态的私有状态。
        invoke(原始输入)
           │
           ▼
        input_schema 过滤  ──►  START ──► 节点1 ──► ... ──► END
           （决定哪些字段能进）         （决定从哪开始跑、跑到哪停）
           │
           ▼
        output_schema 过滤
           │
           ▼
        返回值
"""
from typing import TypedDict
from langgraph.constants import START,END
from langgraph.graph import StateGraph

# 创建状态(模型类)
class MyState(TypedDict):
    query : str
    final_result : str

class Searchstate(TypedDict):
    rag_search_result : str
    web_search_result : str

class InputState(TypedDict):
    query : str

class OutputState(TypedDict):
    final_result : str

# 创建"画布" -> 创建一个Graph对象
graph = StateGraph(
    input_schema=InputState,
    state_schema=MyState,
    output_schema=OutputState #如果不过滤 默认最后是输出的state_schema所限制的Mystate里面的参数
)

# 创建节点1 : RAG搜索
def rag_search_node(state: InputState):
    query = state["query"]
    rag_search_result = f"关于{query}的RAG搜索结果"
    return {"rag_search_result" : rag_search_result}

# 创建节点2 : web搜索
def web_search_node(state: InputState):
    query = state["query"]
    web_search_result = f"关于{query}的web搜索结果"
    return {"web_search_result" : web_search_result}

# 创建节点3 : LLM总结
def final_node(state: Searchstate):
    rag_search_result = state["rag_search_result"]
    web_search_result = state["web_search_result"]
    final_result = f"合并{rag_search_result}和{web_search_result},由LLM总结输出"
    return {"final_result" : final_result}

# 添加节点到画布
graph.add_node(rag_search_node)
graph.add_node(web_search_node)
graph.add_node(final_node)

# 添加边,将各个节点按照执行顺序进行链接
# START:虚拟节点,表示开始节点; END: 虚拟节点, 表示结束节点
graph.add_edge(START,"rag_search_node")
graph.add_edge(START,"web_search_node")
graph.add_edge("rag_search_node","final_node")
graph.add_edge("web_search_node","final_node")
graph.add_edge("final_node",END)

# 对graph进行编译
compiled_graph = graph.compile()

# 执行已经编译的graph对象
result = compiled_graph.invoke(
    {
        "query" : "什么是LangGraph"
    }
)
print(result['final_result'])