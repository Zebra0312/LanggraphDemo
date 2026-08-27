"""
    节点间数据隔离(管中窥豹,实则标注里的字段合并进状态通道集合,只过滤每个节点的视野)

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

        编译时补通道：LangGraph 会扫每个节点的 state 标注，把标注里的字段合并进状态通道集合。
                你的 MyState 没有 rag/web，但 final_node 标了 Searchstate，
                这两个通道就被补上了——这就是"MyState 没有 web_search_result 却能用"的原因。
        运行时过滤：每个节点收到的 state，是按它自己标注的字段过滤过的。
                final 节点标 Searchstate，就只能看到 rag/web，看不到 query。
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

# ASK AI: 为什么这里做了状态隔离,只传入了InputState给节点2,
# 但是节点2还可以检索到web_search_result这个key并且为其赋值?

# AI answer: 这个 demo 里的"隔离"主要是类型层面的声明——节点参数写 state: SearchState，
# 运行时 LangGraph 其实还是把全量状态(LangGraph 会扫每个节点的 state 标注，
# 把标注里的字段合并进状态通道集合。)传进去的，只是通过类型约束让你"只看该看的字段"。
# 如果你想要运行时真正隔离（别的节点确实写不进、读不到某些字段），
# LangGraph 还有 per-node state_schema（节点私有状态）的机制，那是另一种做法

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
print(result)