"""
    输入输出隔离(管理输入输出)
    新增两种schema(input_schema)和(output_schema) 注意大小写 !
"""
from typing import TypedDict
from langgraph.constants import START,END
from langgraph.graph import StateGraph

# 创建状态(模型类)
class MyState(TypedDict):
    query : str
    newQuery : str
    rag_search_result : str
    web_search_result : str
    final_result : str

# 新增输入的状态类和输出的状态类
class InputState(TypedDict):
    query : str
class OutputState(TypedDict):
    final_result : str

# 创建"画布" -> 创建一个Graph对象
graph = StateGraph(
    state_schema = MyState,
    input_schema= InputState,
    output_schema = OutputState,
)

# Ask AI: 请告诉我输入输出的隔离在我的代码里面体现出来了吗 是怎么体现的?
# AI answer:
# 入口按 InputState 收（丢掉 newQuery）→
# 内部按 MyState 跑（节点间传递全量字段）→
# 出口按 OutputState 给（只给 final_result）。
# 三个 print 刚好是这三道门的证据。
# ----------------------------------------
# 有个细节值得注意：你的第二行输出（web_search_node 打印的）也只有 query，但这不是输入隔离的结果，
# 而是执行顺序的结果——rag_search_node 和 web_search_node 是从 START 并行出发的两个分支，
# web 节点启动的那一刻 rag 还没写入结果，所以它只看到 query。而 final_node 是等两个分支都完成后才跑的，
# 所以能看到两个搜索结果。

# 创建节点1 : RAG搜索
def rag_search_node(state: MyState):
    print(f"测试输入控制 : {state}")
    query = state["query"]
    rag_search_result = f"关于{query}的RAG搜索结果"
    return {"rag_search_result" : rag_search_result}

# 创建节点2 : web搜索
def web_search_node(state: MyState):
    print(f"测试输入控制 : {state}")
    query = state["query"]
    web_search_result = f"关于{query}的web搜索结果"
    return {"web_search_result" : web_search_result}

# 创建节点3 : LLM总结
def final_node(state: MyState):
    print(f"测试输入控制 : {state}")
    query = state["query"]
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
        "query" : "什么是LangGraph",
        "newQuery" : "什么是LangChain"
    }
)
print(result)

# 用grandalf包工具把编译好的图"画"出来看
graph_structure = compiled_graph.get_graph()
res = graph_structure.draw_ascii()
print(res)