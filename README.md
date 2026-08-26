# LanggraphDemo
Hands-on demos for learning LangGraph — minimal, runnable examples of stateful agents, workflows, tools, and memory.

LanggraphDemo is a hands-on collection of LangGraph starter demos. Each example is minimal and self-contained, designed to reproduce the core concepts of LangGraph — state management, nodes and edges, agent loops, tool calling, checkpointer memory, human-in-the-loop, and streaming — so you can read, run, and modify them as you learn.



心得体会:

1.`StateGraph` 的三个 schema 参数 = 全量状态(必须) (state_schema)+ 入口门(可选) (input_schema)+ 出口门(可选)(output_schema)；图只有一个状态，门只是决定谁能进来、谁能出去。
