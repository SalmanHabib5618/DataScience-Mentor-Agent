"""
DS Mentor Agent - Fixed Version
Nodes: Router -> Concept / Code
"""

import os
import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def extract_text(content):
    """Handles both plain string and list-of-parts response formats."""
    if isinstance(content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return content


class AgentState(TypedDict):
    query: str
    intent: str
    response: str


def router_node(state: AgentState) -> AgentState:
    prompt = f"""Classify into ONE word: concept, code, or other.
Query: {state['query']}
Answer with one word only."""
    result = llm.invoke(prompt)
    state["intent"] = extract_text(result.content).strip().lower()
    return state


def concept_node(state: AgentState) -> AgentState:
    prompt = f"Explain this DS concept simply with example:\n{state['query']}"
    result = llm.invoke(prompt)
    state["response"] = extract_text(result.content)
    return state


def code_node(state: AgentState) -> AgentState:
    prompt = f"""You are a Python/DS code mentor.
Debug, explain, or write code for this request:
{state['query']}
Give working code + short explanation."""
    result = llm.invoke(prompt)
    state["response"] = extract_text(result.content)
    return state


def route_decision(state: AgentState) -> str:
    if "code" in state["intent"]:
        return "code"
    return "concept"


graph = StateGraph(AgentState)
graph.add_node("router", router_node)
graph.add_node("concept", concept_node)
graph.add_node("code", code_node)

graph.set_entry_point("router")
graph.add_conditional_edges(
    "router", route_decision,
    {"concept": "concept", "code": "code"}
)
graph.add_edge("concept", END)
graph.add_edge("code", END)

app = graph.compile()

if __name__ == "__main__":
    q = input("Ask: ")
    result = app.invoke({"query": q, "intent": "", "response": ""})
    print(result["response"])
