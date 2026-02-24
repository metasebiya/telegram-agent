# graph.py
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_openai import ChatOpenAI
from state import AgentState

load_dotenv()

# --- NODES & ROUTING (Keep these as they were) ---
async def content_creator(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o")
    response = await llm.ainvoke(state["messages"])
    return {"draft_content": response.content, "is_approved": False}

async def approval_node(state: AgentState):
    return state

def route_post(state: AgentState):
    return "finish" if state.get("is_approved") else "stay_paused"

# --- GRAPH BUILDER ---
builder = StateGraph(AgentState)
builder.add_node("creator", content_creator)
builder.add_node("approval", approval_node)
builder.add_edge(START, "creator")
builder.add_edge("creator", "approval")
builder.add_conditional_edges("approval", route_post, {"finish": END, "stay_paused": END})

# --- THE FIX: ASYNC LIFECYCLE ---
@asynccontextmanager
async def get_agent_app():
    """
    Ensures the AsyncSqliteSaver is properly entered before 
    passing it to the compiler.
    """
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:
        # Now 'memory' is the actual BaseCheckpointSaver instance
        yield builder.compile(
            checkpointer=memory,
            interrupt_before=["approval"]
        )