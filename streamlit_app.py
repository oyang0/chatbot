import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot app protected by a password. "
    "Enter the app password to continue."
)

# ---- Password gate ----
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    password = st.text_input("App Password", type="password")

    if st.button("Log in"):
        if password == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    return False


if not check_password():
    st.stop()

# Optional logout button
if st.button("Log out"):
    st.session_state.authenticated = False
    st.rerun()

# Create an OpenAI client using a server-side secret instead of user input.
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Create a session state variable to store chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream the response from OpenAI.
    stream = client.responses.create(
        model="gpt-5.4",
        input=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
        max_output_tokens=32768,
        reasoning={"effort": "none"},
        temperature=0,
        top_p=1,
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})