import streamlit as st
from ds_mentor_agent import app

st.set_page_config(page_title="DS Mentor", page_icon="◆", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0F172A; color: #F8FAFC; }

.hero-title { font-family: 'Lora', serif; font-size: 2rem; font-weight: 700;
  color: #F8FAFC; margin-bottom: 0.1rem; }
.hero-sub { color: #94A3B8; font-size: 0.9rem; margin-bottom: 1.2rem; }

[data-testid="stChatMessage"] {
  background-color: #1E293B; border-radius: 12px; padding: 0.8rem 1rem;
  margin-bottom: 0.6rem; border-left: 3px solid #D4A853;
}

/* Merged input bar container */
.input-bar {
  background-color: #1E293B; border: 1px solid #334155; border-radius: 14px;
  padding: 0.5rem 0.6rem; display: flex; align-items: center; gap: 0.4rem;
}
.input-bar [data-testid="stPopover"] button,
.input-bar .stButton button {
  background-color: transparent !important; color: #D4A853 !important;
  border: 1px solid #334155 !important; border-radius: 50% !important;
  width: 38px !important; height: 38px !important; font-size: 1.1rem !important;
  font-weight: 700 !important; padding: 0 !important;
}
.input-bar [data-testid="stPopover"] button:hover,
.input-bar .stButton button:hover {
  background-color: #334155 !important; border-color: #D4A853 !important;
}
.input-bar .stTextInput input {
  background-color: transparent !important; border: none !important;
  color: #F8FAFC !important; box-shadow: none !important; padding: 0.5rem 0 !important;
}
.input-bar .stTextInput input::placeholder { color: #94A3B8 !important; }
.input-bar .stTextInput > div { border: none !important; background: transparent !important; }

[data-testid="stPopoverBody"] {
  background-color: #1E293B !important; border: 1px solid #334155 !important;
}

.stFileUploader > div > div {
  background-color: #0F172A; border: 1px dashed #334155; border-radius: 8px;
}
.stFileUploader label { color: #94A3B8 !important; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Logo + Header ----------
LOGO_SVG = """
<svg width="46" height="46" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
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
st.markdown('<div class="hero-sub">Your personal Data Science mentor — ask anything.</div>', unsafe_allow_html=True)

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "uploaded_kind" not in st.session_state:
    st.session_state.uploaded_kind = None

# ---------- Render chat history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="◆" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# ---------- Attach (+) control, above chat input ----------
# ---------- Merged input bar: [+] [text] [send] ----------
if st.session_state.get("clear_input"):
    st.session_state.chat_text = ""
    st.session_state.clear_input = False

st.markdown('<div class="input-bar">', unsafe_allow_html=True)
c_plus, c_text, c_send = st.columns([1, 10, 1])

with c_plus:
    with st.popover("➕"):
        st.markdown("**Attach a file**")
        choice = st.radio("Type", ["Code / Text file", "CSV / Data file", "Image"], label_visibility="collapsed")
        if choice == "Code / Text file":
            f = st.file_uploader("Upload code/text", type=["py", "txt", "md", "ipynb"], key="up_code")
        elif choice == "CSV / Data file":
            f = st.file_uploader("Upload data", type=["csv", "tsv", "json"], key="up_data")
        else:
            f = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], key="up_img")

        if f is not None:
            st.session_state.uploaded_file = f
            st.session_state.uploaded_kind = choice
            st.success(f"Attached: {f.name}")

        if st.session_state.uploaded_file is not None:
            if st.button("Remove attachment"):
                st.session_state.uploaded_file = None
                st.session_state.uploaded_kind = None

with c_text:
    st.text_input("msg", key="chat_text", placeholder="Ask your Data Science question...",
                   label_visibility="collapsed")
with c_send:
    send_clicked = st.button("↑", key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.uploaded_file is not None:
    st.caption(f"📎 {st.session_state.uploaded_file.name} will be attached to your next message")

prompt = None
if send_clicked and st.session_state.get("chat_text"):
    prompt = st.session_state.chat_text
    st.session_state.clear_input = True

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    final_query = prompt
    f = st.session_state.uploaded_file
    if f is not None:
        try:
            if st.session_state.uploaded_kind == "Image":
                final_query = f"{prompt}\n\n[An image file '{f.name}' was attached. Guide how to approach analyzing it, since direct image reading isn't available here.]"
            else:
                f.seek(0)
                file_content = f.read().decode("utf-8", errors="ignore")[:3000]
                final_query = f"{prompt}\n\n[Attached file: {f.name}]\n{file_content}"
        except Exception:
            pass
        st.session_state.uploaded_file = None
        st.session_state.uploaded_kind = None

    with st.chat_message("assistant", avatar="◆"):
        with st.spinner("Thinking..."):
            result = app.invoke({"query": final_query, "intent": "", "response": ""})
            st.markdown(result["response"])

    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
