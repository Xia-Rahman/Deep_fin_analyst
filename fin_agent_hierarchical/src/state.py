from typing import TypedDict

class AgentState(TypedDict):
    query: str
    complexity_level: int
    final_response: str
