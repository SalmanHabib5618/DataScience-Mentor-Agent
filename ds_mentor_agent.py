"""
DS Mentor Agent - Full Career Coverage Version
Router -> Specialist prompt (concept/code/data/model/deployment/business/storytelling/career)
"""

import os
import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


import time


def invoke_with_retry(prompt, max_retries=3, delay=3):
    last_error = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay)
    raise last_error


def extract_text(content):
    if isinstance(content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return content


class AgentState(TypedDict):
    query: str
    intent: str
    response: str


BLOCKED_KEYWORDS = ["hack", "exploit", "malware", "illegal", "virus", "ddos"]


def guardrail_node(state: AgentState) -> AgentState:
    query = state["query"].strip()
    lower_query = query.lower()

    if len(query) < 3:
        state["response"] = "Please ask a clearer Data Science question."
        state["intent"] = "blocked"
        return state

    if len(query) > 1500:
        state["response"] = "Your question is too long. Please shorten it."
        state["intent"] = "blocked"
        return state

    if any(word in lower_query for word in BLOCKED_KEYWORDS):
        state["response"] = "I can only help with safe, learning-focused Data Science topics."
        state["intent"] = "blocked"
        return state

    if "ignore previous instructions" in lower_query or "ignore all instructions" in lower_query:
        state["response"] = "I can only help with Data Science learning topics."
        state["intent"] = "blocked"
        return state

    state["intent"] = "pass"
    return state


def guardrail_decision(state: AgentState) -> str:
    return "blocked" if state["intent"] == "blocked" else "pass"


INTENTS = ["concept", "code", "data", "model", "deployment", "business", "storytelling", "career", "tools"]

PERSONA = """You are a Data Science teacher and mentor with 28+ years of experience
across Data Science, Machine Learning, Generative AI, and Agentic AI.
You believe: Data Science = Mathematics + Computer Science + Domain Expertise
(plus, in the AI era, a 4th pillar: AI/LLM Tool Fluency).
The student is a complete beginner. Always teach step-by-step, in simple language,
with small examples before technical depth. Be encouraging and patient, like a
real mentor guiding a junior through their first years."""

SYSTEM_PROMPTS = {
    "concept": PERSONA + "\nTask: Explain the concept simply, step-by-step, with a beginner example.",
    "code": PERSONA + "\nTask: Debug or write working code. Explain each part simply, step-by-step.",
    "data": PERSONA + "\nTask: Guide data cleaning/EDA/feature engineering step-by-step for beginners.",
    "model": PERSONA + "\nTask: Explain model choice, training, and evaluation step-by-step, simply.",
    "deployment": PERSONA + "\nTask: Explain deployment/MLOps production basics step-by-step for beginners.",
    "business": PERSONA + "\nTask: Convert vague business problems into clear DS problems, step-by-step.",
    "storytelling": PERSONA + "\nTask: Teach presenting results using the 'So What?' framework, step-by-step.",
    "career": PERSONA + "\nTask: Give a practical, encouraging, step-by-step career roadmap/advice for the AI era.",
    "tools": PERSONA + "\nTask: Explain the DS/AI-era tool (what it is, why it's used, and how to start using it) step-by-step for a beginner, with a simple example.",
}


def router_node(state: AgentState) -> AgentState:
    options = ", ".join(INTENTS)
    prompt = f"""Classify the query into exactly ONE of these words: {options}
Query: {state['query']}
Answer with one word only."""
    result = invoke_with_retry(prompt)
    intent = extract_text(result.content).strip().lower()
    state["intent"] = intent if intent in INTENTS else "concept"
    return state


def assist_node(state: AgentState) -> AgentState:
    system_prompt = SYSTEM_PROMPTS[state["intent"]]
    prompt = f"{system_prompt}\n\nBeginner's question: {state['query']}"
    try:
        result = invoke_with_retry(prompt)
        state["response"] = extract_text(result.content)
    except Exception as e:
        state["response"] = f"Sorry, something went wrong reaching the AI model. Please try again shortly. ({type(e).__name__})"
    return state


graph = StateGraph(AgentState)
graph.add_node("guardrail", guardrail_node)
graph.add_node("router", router_node)
graph.add_node("assist", assist_node)

graph.set_entry_point("guardrail")
graph.add_conditional_edges(
    "guardrail", guardrail_decision,
    {"blocked": END, "pass": "router"}
)
graph.add_edge("router", "assist")
graph.add_edge("assist", END)

app = graph.compile()

if __name__ == "__main__":
    q = input("Ask: ")
    result = app.invoke({"query": q, "intent": "", "response": ""})
    print(f"[{result['intent']}]\n{result['response']}")
