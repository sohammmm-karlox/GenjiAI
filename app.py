import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3-flash-preview"  # check the current model name in Google AI Studio

# ---------- Our own prompt design (the "brain" of GenjiAI) ----------
BASE_PROMPT = """You are GenjiAI, a friendly assistant for college students.
You talk in Gen Z slang (examples: no cap, lowkey, bet, vibe, slay, fr, bruh,
rizz, goated, it's giving...). Keep replies short, clear and helpful.
Always keep the actual advice accurate - slang is the style, not an excuse
to be wrong. Use bullet points for steps."""

MODES = {
    "Study": "Focus on studies: explain concepts simply with examples, "
             "give study plans, exam tips and memory tricks.",
    "Health": "Focus on student wellness: sleep, stress, food, exercise. "
              "NEVER diagnose, never suggest medicine or dosage. For anything "
              "serious, tell the student to see a doctor or counselor.",
    "Chill": "Casual chat and motivation, but stay positive and respectful.",
}

SLANG = {
    "Light": "Use a little slang.",
    "Medium": "Use a good amount of slang.",
    "Max": "Use heavy Gen Z slang in every sentence.",
}

# ---------- Safety layer ----------
CRISIS_WORDS = ["suicide", "kill myself", "end my life", "self harm", "self-harm"]
CRISIS_MSG = (
    "Hey, I'm really glad you said this, and you matter. I'm just an AI, so "
    "please talk to someone right now: a trusted friend, family member or your "
    "college counselor. In India you can call Tele-MANAS at 14416 (free, 24x7)."
)


def build_system_prompt(mode, level):
    return f"{BASE_PROMPT}\n\nMode: {MODES[mode]}\nSlang level: {SLANG[level]}"


# ---------- UI ----------
st.set_page_config(page_title="GenjiAI", page_icon="🔥")
st.title("🔥 GenjiAI")
st.caption("Your Gen Z study & wellness buddy")

mode = st.sidebar.selectbox("Mode", list(MODES.keys()))
level = st.sidebar.select_slider("Slang level", list(SLANG.keys()), value="Medium")
if st.sidebar.button("Clear chat"):
    st.session_state.history = []

if "history" not in st.session_state:
    st.session_state.history = []

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.write(text)

user_msg = st.chat_input("Ask anything...")
if user_msg:
    st.session_state.history.append(("user", user_msg))
    with st.chat_message("user"):
        st.write(user_msg)

    if any(w in user_msg.lower() for w in CRISIS_WORDS):
        reply = CRISIS_MSG
    else:
        contents = [
            types.Content(
                role="user" if r == "user" else "model",
                parts=[types.Part(text=t)],
            )
            for r, t in st.session_state.history
        ]
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=build_system_prompt(mode, level)
                ),
            )
            reply = resp.text
        except Exception as e:
            reply = f"Oops, something broke: {e}"

    st.session_state.history.append(("assistant", reply))
    with st.chat_message("assistant"):
        st.write(reply)
