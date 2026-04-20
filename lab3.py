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


## decalre state
class State(TypedDict):
      messages: Annotated[list, add_messages]

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
## browser and its tools 
async_browser =  create_async_playwright_browser(headless=False)  # headful mode
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()
toolsDict = {tool.name:tools for tool in tools}

def main():
    print("Hello from langgraph!")
    load_dotenv(override=True)
    nest_asyncio.apply()
    graph_builder = StateGraph(State)
    # If you get a NotImplementedError here or later, see the Heads Up at the top of the notebook

    
    print(toolsDict)




if __name__ == "__main__":
    main()
