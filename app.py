import streamlit as st
from ds_mentor_agent import app

st.set_page_config(page_title="DS Mentor", page_icon="◆", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0F172A; color: #F8FAFC; }

.hero-title { font-family: 'Lora', serif; font-size: 2.4rem; font-weight: 700;
  color: #F8FAFC; margin-bottom: 0.2rem; }
.hero-sub { color: #94A3B8; font-size: 1rem; margin-bottom: 2rem; }

.stTextInput > div > div > input {
  background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155;
  border-radius: 8px; padding: 0.7rem;
}

.stButton > button {
  background-color: #D4A853; color: #0F172A; border: none;
  border-radius: 8px; font-weight: 600; padding: 0.5rem 1.5rem;
}
.stButton > button:hover { background-color: #E8BE6D; color: #0F172A; }

.stFileUploader > div > div {
  background-color: #1E293B; border: 1px dashed #334155; border-radius: 8px;
}
.stFileUploader label { color: #94A3B8 !important; font-size: 0.85rem; }

.response-card {
  background-color: #1E293B; border-left: 3px solid #D4A853;
  border-radius: 8px; padding: 1.2rem; margin-top: 1.2rem;
  color: #E2E8F0; line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ---------- Logo (inline SVG) ----------
LOGO_SVG = """
<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
  <circle cx="30" cy="30" r="29" fill="#0F172A" stroke="#D4A853" stroke-width="1.5"/>
  <circle cx="20" cy="22" r="3.2" fill="#D4A853"/>
  <circle cx="40" cy="22" r="3.2" fill="#D4A853"/>
  <circle cx="30" cy="40" r="3.2" fill="#D4A853"/>
  <line x1="20" y1="22" x2="40" y2="22" stroke="#D4A853" stroke-width="1.2"/>
  <line x1="20" y1="22" x2="30" y2="40" stroke="#D4A853" stroke-width="1.2"/>
  <line x1="40" y1="22" x2="30" y2="40" stroke="#D4A853" stroke-width="1.2"/>
</svg>
"""

col1, col2 = st.columns([1, 6])
with col1:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
with col2:
    st.markdown('<div class="hero-title">DS Mentor</div>', unsafe_allow_html=True)

st.markdown('<div class="hero-sub">Your personal guide through Data Science — concepts, code, and clarity.</div>', unsafe_allow_html=True)

# ---------- Chat history (custom feature) ----------
if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask your Data Science question", placeholder="e.g. Explain bias-variance tradeoff")

with st.expander("➕ Attach a file (code / CSV / notes)", expanded=False):
    uploaded_file = st.file_uploader("Attach", type=["py", "csv", "txt", "md"], label_visibility="collapsed")

col_a, col_b = st.columns([1, 5])
with col_a:
    ask = st.button("Ask")
with col_b:
    clear = st.button("Clear history")

if clear:
    st.session_state.history = []

if ask and query:
    final_query = query
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8", errors="ignore")[:3000]
            final_query = f"{query}\n\n[Attached file: {uploaded_file.name}]\n{file_content}"
        except Exception:
            pass
    result = app.invoke({"query": final_query, "intent": "", "response": ""})
    st.session_state.history.insert(0, {"q": query, "a": result["response"], "intent": result["intent"]})

# ---------- Display responses ----------
for item in st.session_state.history:
    st.markdown(f"""
    <div class="response-card">
      <b style="color:#D4A853;">You asked:</b> {item['q']}<br><br>
      {item['a']}
    </div>
    """, unsafe_allow_html=True)
