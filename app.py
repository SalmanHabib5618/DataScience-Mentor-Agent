import streamlit as st
from ds_mentor_agent import app

st.set_page_config(page_title="DS Mentor", page_icon="🧠", layout="centered")
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">', unsafe_allow_html=True)

# ---------- Warm Paper theme ----------
BG = "#FDFBF7"
CARD = "#FFFFFF"
BORDER = "#EDE3D3"
TEXT = "#2B2620"
SUB = "#A99E8C"
ACCENT = "#B45309"
ACCENT_TEXT = "#FFFFFF"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background-color: {BG}; color: {TEXT}; }}

.header-wrap {{ text-align: center; margin-bottom: 1.2rem; }}
.header-row {{ display: flex; align-items: center; justify-content: center; gap: 0.6rem; }}
.hero-title {{ font-family: 'Lora', serif; font-size: 2rem; font-weight: 700; color: {TEXT}; }}
.hero-sub {{ color: {SUB}; font-size: 0.9rem; margin-top: 0.1rem; }}

.bubble-user {{
  background-color: {ACCENT}; color: {ACCENT_TEXT}; border-radius: 14px 14px 2px 14px;
  padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 75%; margin-left: auto;
}}
.bubble-assistant {{
  background-color: {CARD}; color: {TEXT}; border: 1px solid {BORDER};
  border-radius: 14px 14px 14px 2px; padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 75%;
}}
.row-user {{ display: flex; justify-content: flex-end; }}
.row-assistant {{ display: flex; justify-content: flex-start; }}

.input-bar {{
  background-color: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
  padding: 0.4rem 0.6rem; display: flex; align-items: center; gap: 0.4rem;
}}
.input-bar [data-testid="stPopover"] button, .input-bar .stButton button {{
  background-color: #FCEEDD !important; color: {ACCENT} !important;
  border: 1px solid {BORDER} !important; border-radius: 50% !important;
  width: 38px !important; height: 38px !important; font-size: 1.1rem !important; padding: 0 !important;
}}
.input-bar .stButton button:last-child {{
  background-color: {ACCENT} !important; color: #fff !important;
}}
.input-bar .stTextInput input {{
  background-color: transparent !important; border: none !important;
  color: {TEXT} !important; box-shadow: none !important;
}}
.input-bar .stTextInput input::placeholder {{ color: {SUB} !important; }}
.input-bar .stTextInput > div {{ border: none !important; background: transparent !important; }}
[data-testid="stPopoverBody"] {{ background-color: {CARD} !important; border: 1px solid {BORDER} !important; }}
.stFileUploader > div > div {{ background-color: {BG}; border: 1px dashed {BORDER}; border-radius: 8px; }}

/* Force input row to stay side-by-side on mobile (prevents Streamlit's default column stacking) */
[data-testid="stHorizontalBlock"] {{
  flex-wrap: nowrap !important; align-items: center !important; gap: 0.3rem !important;
}}
[data-testid="stHorizontalBlock"] > div:nth-of-type(1) {{ flex: 0 0 44px !important; min-width: 44px !important; width: 44px !important; }}
[data-testid="stHorizontalBlock"] > div:nth-of-type(2) {{ flex: 1 1 auto !important; min-width: 0 !important; }}
[data-testid="stHorizontalBlock"] > div:nth-of-type(3) {{ flex: 0 0 44px !important; min-width: 44px !important; width: 44px !important; }}
</style>
""", unsafe_allow_html=True)

# ---------- Header: logo + name + description, centered ----------
LOGO_SVG = f"""
<svg width="44" height="44" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
  <circle cx="30" cy="30" r="29" fill="{BG}" stroke="{ACCENT}" stroke-width="1.5"/>
  <circle cx="20" cy="22" r="3.2" fill="{ACCENT}"/>
  <circle cx="40" cy="22" r="3.2" fill="{ACCENT}"/>
  <circle cx="30" cy="40" r="3.2" fill="{ACCENT}"/>
  <line x1="20" y1="22" x2="40" y2="22" stroke="{ACCENT}" stroke-width="1.2"/>
  <line x1="20" y1="22" x2="30" y2="40" stroke="{ACCENT}" stroke-width="1.2"/>
  <line x1="40" y1="22" x2="30" y2="40" stroke="{ACCENT}" stroke-width="1.2"/>
</svg>
"""
st.markdown(f"""
<div class="header-wrap">
  <div class="header-row">{LOGO_SVG}<div class="hero-title">DS Mentor</div></div>
  <div class="hero-sub">Your personal Data Science mentor — ask anything.</div>
</div>
""", unsafe_allow_html=True)

# ---------- State ----------
for key, default in [("messages", []), ("uploaded_file", None), ("uploaded_kind", None), ("clear_input", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Chat history ----------
for msg in st.session_state.messages:
    row = "row-user" if msg["role"] == "user" else "row-assistant"
    bubble = "bubble-user" if msg["role"] == "user" else "bubble-assistant"
    st.markdown(f'<div class="{row}"><div class="{bubble}">{msg["content"]}</div></div>', unsafe_allow_html=True)

# ---------- Merged input bar: [+] [text] [send] ----------
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
