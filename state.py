import operator
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # 'add_messages' ensures new messages are appended to history, not replaced
    messages: Annotated[List[BaseMessage], operator.add]
    draft_content: str
    is_approved: bool
    revision_count: int