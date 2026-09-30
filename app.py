import streamlit as st
from ds_mentor_agent import app

st.set_page_config(page_title="DS Mentor", page_icon="🧠", layout="wide")

# ---------- Theme definitions ----------
THEMES = {
    "Midnight Gold": {
        "bg": "#0F172A", "card": "#1E293B", "border": "#334155",
        "text": "#F8FAFC", "sub": "#94A3B8", "accent": "#D4A853", "accent_text": "#0F172A",
    },
    "Royal Purple": {
        "bg": "#150E29", "card": "#241A44", "border": "#3D2E68",
        "text": "#F5F3FF", "sub": "#B9A9E8", "accent": "#A78BFA", "accent_text": "#150E29",
    },
    "Forest Calm": {
        "bg": "#0B1F17", "card": "#163527", "border": "#2A5A41",
        "text": "#F0FAF5", "sub": "#8FC9AC", "accent": "#4ADE80", "accent_text": "#0B1F17",
    },
    "Clean Light": {
        "bg": "#F8FAFC", "card": "#FFFFFF", "border": "#E2E8F0",
        "text": "#0F172A", "sub": "#64748B", "accent": "#2563EB", "accent_text": "#FFFFFF",
    },
}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight Gold"
T = THEMES[st.session_state.theme_name]

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🧠 DS Mentor")
    st.caption("Your personal Data Science mentor")
    st.session_state.theme_name = st.selectbox("Theme", list(THEMES.keys()),
                                                 index=list(THEMES.keys()).index(st.session_state.theme_name))
    T = THEMES[st.session_state.theme_name]
    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- CSS (theme-driven) ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background-color: {T['bg']}; color: {T['text']}; }}
section[data-testid="stSidebar"] {{ background-color: {T['card']}; border-right: 1px solid {T['border']}; }}

.hero-title {{ font-family: 'Lora', serif; font-size: 1.8rem; font-weight: 700; color: {T['text']}; }}
.hero-sub {{ color: {T['sub']}; font-size: 0.9rem; margin-bottom: 1rem; }}

.bubble-user {{
  background-color: {T['accent']}; color: {T['accent_text']}; border-radius: 14px 14px 2px 14px;
  padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 75%; margin-left: auto; text-align: left;
}}
.bubble-assistant {{
  background-color: {T['card']}; color: {T['text']}; border: 1px solid {T['border']};
  border-radius: 14px 14px 14px 2px; padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 75%;
}}
.row-user {{ display: flex; justify-content: flex-end; }}
.row-assistant {{ display: flex; justify-content: flex-start; }}

.input-bar {{
  background-color: {T['card']}; border: 1px solid {T['border']}; border-radius: 14px;
  padding: 0.4rem 0.6rem; display: flex; align-items: center; gap: 0.4rem;
}}
.input-bar [data-testid="stPopover"] button, .input-bar .stButton button {{
  background-color: transparent !important; color: {T['accent']} !important;
  border: 1px solid {T['border']} !important; border-radius: 50% !important;
  width: 38px !important; height: 38px !important; font-size: 1.1rem !important; padding: 0 !important;
}}
.input-bar .stTextInput input {{
  background-color: transparent !important; border: none !important;
  color: {T['text']} !important; box-shadow: none !important;
}}
.input-bar .stTextInput input::placeholder {{ color: {T['sub']} !important; }}
.input-bar .stTextInput > div {{ border: none !important; background: transparent !important; }}
[data-testid="stPopoverBody"] {{ background-color: {T['card']} !important; border: 1px solid {T['border']} !important; }}
.stFileUploader > div > div {{ background-color: {T['bg']}; border: 1px dashed {T['border']}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="hero-title">DS Mentor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Ask anything about your Data Science journey.</div>', unsafe_allow_html=True)

# ---------- State ----------
for key, default in [("messages", []), ("uploaded_file", None), ("uploaded_kind", None), ("clear_input", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Render chat history ----------
chat_area = st.container()
with chat_area:
    for msg in st.session_state.messages:
        row = "row-user" if msg["role"] == "user" else "row-assistant"
        bubble = "bubble-user" if msg["role"] == "user" else "bubble-assistant"
        st.markdown(f'<div class="{row}"><div class="{bubble}">{msg["content"]}</div></div>', unsafe_allow_html=True)

# ---------- Merged input bar ----------
if st.session_state.clear_input:
    st.session_state.chat_text = ""
    st.session_state.clear_input = False

st.markdown('<div class="input-bar">', unsafe_allow_html=True)
c_plus, c_text, c_send = st.columns([1, 10, 1])

with c_plus:
    with st.popover("➕"):
        st.markdown("**Attach a file**")
        choice = st.radio("Type", ["Code / Text", "CSV / Data", "Image"], label_visibility="collapsed")
        key_map = {"Code / Text": ("up_code", ["py", "txt", "md", "ipynb"]),
                   "CSV / Data": ("up_data", ["csv", "tsv", "json"]),
                   "Image": ("up_img", ["png", "jpg", "jpeg"])}
        k, types = key_map[choice]
        f = st.file_uploader("Upload", type=types, key=k, label_visibility="collapsed")
        if f is not None:
            st.session_state.uploaded_file = f
            st.session_state.uploaded_kind = choice
            st.success(f"Attached: {f.name}")
        if st.session_state.uploaded_file is not None and st.button("Remove attachment"):
            st.session_state.uploaded_file = None
            st.session_state.uploaded_kind = None

with c_text:
    st.text_input("msg", key="chat_text", placeholder="Ask your Data Science question...",
                   label_visibility="collapsed")
with c_send:
    send_clicked = st.button("↑", key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.uploaded_file is not None:
    st.caption(f"📎 {st.session_state.uploaded_file.name} attached")

prompt = None
if send_clicked and st.session_state.get("chat_text"):
    prompt = st.session_state.chat_text
    st.session_state.clear_input = True

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    final_query = prompt
    f = st.session_state.uploaded_file
    if f is not None:
        try:
            if st.session_state.uploaded_kind == "Image":
                final_query = f"{prompt}\n\n[Image '{f.name}' attached. Guide analysis approach since direct image reading isn't available.]"
            else:
                f.seek(0)
                file_content = f.read().decode("utf-8", errors="ignore")[:3000]
                final_query = f"{prompt}\n\n[Attached file: {f.name}]\n{file_content}"
        except Exception:
            pass
        st.session_state.uploaded_file = None
        st.session_state.uploaded_kind = None

    with st.spinner("Thinking..."):
        result = app.invoke({"query": final_query, "intent": "", "response": ""})

    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
    st.rerun()
