"""
    创建state类TypedDict[官方推荐]

    状态类的对象是字典 使用 [键] or get操作 , 状态类的对象是BaseModel , 使用 .属性

    接下来的例子，以一个基于RAG的问答系统为例，来做一个快速入门展示。
    该问答系统需要实现的功能如下：当接收用户问题之后，先分别进行 联网搜索 和 基于知识库 检索，得到结果之后，使用 大语言模型 进行总结回答。

              --->>    联网搜索    ----
    用      --                         ---
    户  ----                               ----发送---- >> LLM回复
    输      --                         ---
    入         --->>  基于知识库RAG ----

"""

from typing import TypedDict
from langgraph.constants import START,END
from langgraph.graph import StateGraph

# 创建状态(模型类) -> Basemodel 和 TypedDict[官方推荐]
class MyState(TypedDict):
    query : str
    rag_search_result : str
    web_search_result : str
    final_result : str

# 创建"画布" -> 创建一个Graph对象
graph = StateGraph(state_schema=MyState)

# 创建节点1 : RAG搜索
def rag_search_node(state: MyState):
    query = state["query"]
    rag_search_result = f"关于{query}的RAG搜索结果"
    return {"rag_search_result" : rag_search_result}

# 创建节点2 : web搜索
def web_search_node(state: MyState):
    query = state["query"]
    web_search_result = f"关于{query}的web搜索结果"
    return {"web_search_result" : web_search_result}

# 创建节点3 : LLM总结
def final_node(state: MyState):
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
        "query" : "什么是LangGraph"
    }
)
print(result)

# 用grandalf包工具把编译好的图"画"出来看
graph_structure = compiled_graph.get_graph()
res = graph_structure.draw_ascii()
print(res)
#                   +-----------+
#                   | __start__ |
#                   +-----------+
#                 ***            ***
#               **                  **
#             **                      **
# +-----------------+           +-----------------+
# | rag_search_node |           | web_search_node |
# +-----------------+           +-----------------+
#                 ***            ***
#                    **        **
#                      **    **
#                   +------------+
#                   | final_node |
#                   +------------+
#                         *
#                         *
#                         *
#                    +---------+
#                    | __end__ |
#                    +---------+