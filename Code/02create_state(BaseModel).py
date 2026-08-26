"""
状态类的对象是BaseModel , 使用 .属性访问
"""
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel

# 创建状态,状态类的对象是BaseModel , 使用 .属性访问
class MyState(BaseModel):
    query : str
    rag_search_result : str
    web_search_result : str
    final_result : str

# 创建"画布" -> 创建一个Graph对象
graph = StateGraph(state_schema=MyState)

# 创建节点1 : rag搜索
def rag_search_node(state : MyState):
    # 查询用户的输入
    # BaseModel的子类状态类中的属性 就真当 属性看 -> 状态类对象.属性名
    query = state.query
    rag_search_result = f"关于{query}的RAG搜索结果"
    return {"rag_search_result" : rag_search_result}
# 创建节点2 : web搜索
def web_search_node(state : MyState):
    # 查询用户的输入
    query = state.query
    web_search_result = f"关于{query}的web搜索结果"
    return {"web_search_result" : web_search_result}
# 创建节点3 : LLM总结
def final_node(state : MyState):
    # 查询 web 和 rag 节点的结果
    rag_search_result = state.rag_search_result
    web_search_result = state.web_search_result
    final_result = f"合并{rag_search_result}和{web_search_result},由LLM总结输出"
    return {"final_result" : final_result}


# 添加节点到画布
graph.add_node(rag_search_node)
graph.add_node(web_search_node)
graph.add_node(final_node)

# 描边
graph.add_edge(START, "web_search_node")
graph.add_edge(START, "rag_search_node")
graph.add_edge("web_search_node", "final_node")
graph.add_edge("rag_search_node", "final_node")
graph.add_edge("final_node", END)

# 对graph进行编译
compiled_graph = graph.compile()

# 执行已经编译的graph对象
# Error:pydantic_core._pydantic_core.ValidationError: 3 validation errors for MyState
# BaseModel 定义的字段默认都是必填的，所以 pydantic 直接抛 ValidationError
# result = compiled_graph.invoke(
#     {
#         "query" : "什么是LangGraph"
#     }
# )

# 解决方案 1 : 当使用 basemodel的方式定义状态类,状态类中的属性必须有初始值 ! [typed_dict的方式则不需要]
result = compiled_graph.invoke(
    {
        "query" : "什么是LangGraph",
        "rag_search_result" : "",
        "web_search_result" : "",
        "final_result" : "",
    }
)

print(result)