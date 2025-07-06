# app.py
import streamlit as st

st.set_page_config(page_title="Schedule AI", layout="centered")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]
if "suggestions" not in st.session_state:
    st.session_state.suggestions = ["Tuesday at 2 PM", "Wednesday at 10 AM", "Thursday at 3 PM"]
if "appointment" not in st.session_state:
    st.session_state.appointment = None

# --- Header ---
st.markdown("## 🗓 Schedule AI")
st.markdown("I can help you schedule meetings in your calendar. Just tell me what you need.")

# --- Chat history ---
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    else:
        st.chat_message("user").write(msg["content"])

# --- Suggestion buttons ---
with st.container():
    cols = st.columns(len(st.session_state.suggestions))
    for i, suggestion in enumerate(st.session_state.suggestions):
        if cols[i].button(suggestion):
            # Simulate user picking a time
            st.session_state.messages.append({"role": "user", "content": suggestion})
            # Stubbed “assistant” response: show appointment preview
            st.session_state.appointment = {
                "title": "Meeting with Alex",
                "when": f"Tuesday, July 23, {suggestion}",
                # you can swap this for any local image or URL
                "image_url": "https://via.placeholder.com/800x200.png?text=Calendar+Preview"
            }
            st.rerun()

# --- Text input for free chat ---
user_input = st.chat_input("Type a message")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # <<< STUBBED BACKEND LOGIC >>>
    # Instead of calling your real LLM or calendar API, just echo or send a canned reply:
    assistant_reply = (
        "Got it! (This is a stubbed response—replace me with your LLM or API call.)\n"
        "Try clicking one of the suggested times above."
    )
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

# --- Appointment preview card + Confirm button ---
if st.session_state.appointment:
    st.markdown("---")
    with st.container():
        st.image(st.session_state.appointment["image_url"], use_container_width=True)
        st.markdown(
            f"### {st.session_state.appointment['title']}\n"
            f"**{st.session_state.appointment['when']}**"
        )
        if st.button("Confirm"):
            # <<< STUBBED BOOKING ACTION >>>
            st.success("✅ (Stub) Your meeting has been booked!")

