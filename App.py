import streamlit as st
from ds_mentor_agent import app

st.title("DS Mentor Agent")
query = st.text_input("Ask your Data Science question:")

if st.button("Ask") and query:
    result = app.invoke({"query": query, "intent": "", "response": ""})
    st.write(result["response"])
