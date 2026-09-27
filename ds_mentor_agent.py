"""
DS Mentor Agent - Full Version
Nodes: Router -> Concept / Code / Fallback
"""
import streamlit as st
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")


class AgentState(TypedDict):
    query: str
    intent: str
    response: str


def router_node(state: AgentState) -> AgentState:
    prompt = f"""Classify into ONE word: concept, code, or other.
Query: {state['query']}
Answer with one word only."""
    result = llm.invoke(prompt)
    state["intent"] = result.content.strip().lower()
    return state


def concept_node(state: AgentState) -> AgentState:
    prompt = f"Explain this DS concept simply with example:\n{state['query']}"
    state["response"] = llm.invoke(prompt).content
    return state


def code_node(state: AgentState) -> AgentState:
    prompt = f"""You are a Python/DS code mentor.
Debug, explain, or write code for this request:
{state['query']}
Give working code + short explanation."""
    state["response"] = llm.invoke(prompt).content
    return state


def fallback_node(state: AgentState) -> AgentState:
    state["response"] = "Query type not supported yet."
    return state


def route_decision(state: AgentState) -> str:
    if "concept" in state["intent"]:
        return "concept"
    if "code" in state["intent"]:
        return "code"
    return "fallback"


graph = StateGraph(AgentState)
graph.add_node("router", router_node)
graph.add_node("concept", concept_node)
graph.add_node("code", code_node)
graph.add_node("fallback", fallback_node)

graph.set_entry_point("router")
graph.add_conditional_edges(
    "router", route_decision,
    {"concept": "concept", "code": "code", "fallback": "fallback"}
)
graph.add_edge("concept", END)
graph.add_edge("code", END)
graph.add_edge("fallback", END)

app = graph.compile()

if __name__ == "__main__":
    q = input("Ask: ")
    result = app.invoke({"query": q, "intent": "", "response": ""})
    print(result["response"])
