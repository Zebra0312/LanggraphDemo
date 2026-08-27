"""
    测试：节点的输出
    注意：多个节点并行执行时，多个并行执行节点所返回的状态（字典）不能包含相同的键（属性）
    否则报错：At key 'query': Can receive only one value per step.
"""
from typing import TypedDict
from langgraph.constants import START,END
from langgraph.graph import StateGraph

class MyState(TypedDict):
    query:str
    file_result:str
    web_result:str
    final_answer:str

def query_web(state:MyState)->dict:
    """
    做网络搜索，返回搜索结果
    :return:
    """
    # 1、错误演示：直接return整个state，而非当前节点增量修改的状态
    query = state['query']
    state['web_result'] = f'{query}的网络搜索结果'
    return state

def query_file(state:MyState)->dict:
    """
    做文件搜索，返回搜索结果
    :return:
    """
    query = state['query']
    state['file_result'] = f'{query}的文件搜索结果'
    return state

def answer(state:MyState)->dict:
    """
    返回最终的答案
    :return:
    """
    web_result = state['web_result']
    file_result = state['file_result']
    final_answer = f'LLM基于{web_result}，{file_result} 的最终结果'
    state['final_answer'] = final_answer
    return state

graph = StateGraph(state_schema=MyState)
graph.add_node(answer)
graph.add_node(query_web)
graph.add_node(query_file)


# query_web和query_file并行执行
# graph.add_edge(START,'query_web')
# graph.add_edge(START,'query_file')
# graph.add_edge('query_web','answer')
# graph.add_edge('query_file','answer')

# query_web和query_file串行执行
graph.add_edge(START,'query_web')
graph.add_edge("query_web",'query_file')
graph.add_edge("query_file",'answer')
graph.add_edge("answer",END)


compiled_graph = graph.compile()
res = compiled_graph.invoke({"query":"什么是Langgraph"})
print(res)