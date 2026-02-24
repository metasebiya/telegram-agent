import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from state import AgentState

load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o")

# --- NODES ---

async def content_creator(state: AgentState):
    """Generates the post draft based on message history."""
    messages = state["messages"]
    
    # Simple prompt logic
    response = await llm.ainvoke(messages)
    
    return {
        "draft_content": response.content,
        "revision_count": state.get("revision_count", 0) + 1,
        "is_approved": False # Reset approval for new drafts
    }

async def human_approval(state: AgentState):
    """
    This node is a 'passive' node. 
    The graph stops HERE because of the interrupt.
    """
    return state

# --- ROUTING LOGIC ---

def should_publish(state: AgentState):
    """Check if the user has approved the post."""
    if state.get("is_approved"):
        return "publisher"
    return END # If not approved, wait for next user input

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

# Add our nodes
workflow.add_node("creator", content_creator)
workflow.add_node("approval", human_approval)

# We don't need a formal 'publisher' node if main.py handles the API call,
# but we use 'approval' as the fork point.

workflow.add_edge(START, "creator")
workflow.add_edge("creator", "approval")

# Conditional path
workflow.add_conditional_edges(
    "approval",
    should_publish,
    {
        "publisher": END, # In main.py, we detect if 'publisher' was reached
        END: END
    }
)

# --- PERSISTENCE ---
# This creates a local SQLite file to store every step for 'Time Travel'
memory = SqliteSaver.from_conn_string("./checkpoints/state.db")

# Compile the graph with an INTERRUPT
app = workflow.compile(
    checkpointer=memory, 
    interrupt_before=["approval"] 
)