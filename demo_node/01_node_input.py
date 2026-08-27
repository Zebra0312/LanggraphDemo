"""
    测试：节点的输入，即节点函数的三个参数（ state<状态类型>(最常用),
                                    config<RunnableConfig>,
                                    runtime<Runtime>）
"""
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

class MyState(TypedDict):
    query : str
    response : str

class LLMResponse:
    def invoke(self):
        return "AI Response: HelloWorld"



def node(state: MyState, config: RunnableConfig, runtime: Runtime):
# 测试获取config里面的数据
    configurable = config["configurable"]
    thread_id = configurable["thread_id"]
    test_config = configurable["test_config"]
    print(f"{thread_id=}, {test_config=}")
# 测试runtime对象
    llm = runtime.context["llm"]
    llm_response = llm.invoke()

    return {"response" : llm_response}



builder = StateGraph(state_schema=MyState)

builder.add_node(node)

# builder.add_edge(START,"node") 等价于 builder.set_entry_point("node")
builder.set_entry_point("node")
builder.add_edge("node", END)

graph = builder.compile()

# 创建配置(字典)
config = {
    "configurable" : {
        "thread_id" : "abc",
        "test_config": "config message"
    },
}


# 创建LLMResponses实例
llm = LLMResponse()
# 将llm存储到字典中，在传输到节点中
context = {
    "llm": llm
}



result = graph.invoke(
    {"query": "你会langgraph吗?"},  # 给state赋值
    config=config, # 给config赋值
    context=context
)

print(result)