from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import os
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import requests
import nest_asyncio

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

import asyncio 

load_dotenv(override=True)
# nest_asyncio.apply()langsm

## decalre state
class State(TypedDict):
      messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

##custom tool
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = os.getenv("PUSHOVER_URL")
def push(text: str):
      """Makes a push notification to user"""
      requests.post(pushover_url , data = {"token":pushover_token, "user":pushover_user, "message":text})
push_tool = Tool(
      name="push_notification",
      func=push,
      description="Invoked when we need to send a notification to user"
)

##declare tools 
async_browser =  create_async_playwright_browser(headless=False)
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()
tool_dict = {tool.name:tool for tool in tools}
#     navigate_tool = tool_dict.get("navigate_browser")
#     await navigate_tool.arun({"url": "https://www.cnn.com"})
all_tools = tools + [push_tool]


## chatbot niode
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(all_tools)

def chatbot(state:State):
     return {"messages":[llm_with_tools.invoke(state["messages"])]}

#nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=all_tools))

#edges
graph_builder.add_conditional_edges( "chatbot", tools_condition, "tools")
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
img = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(img)


config = {"configurable":{"thread_id":"10"}}
def chat(user_input: str, history):
     result = graph.invoke({"messages":[{"role":"user", "content":user_input}]},config=config)
     return result["messages"][-1].content
gr.ChatInterface(chat).launch()

async def main():
    print("Hello from langgraph!")

  
if __name__ == "__main__":
    asyncio.run(main())