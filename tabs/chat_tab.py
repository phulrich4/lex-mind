# tabs/chat_tab.py
import streamlit as st
import replicate
import os

# Setze API Key (aus Streamlit Secrets, NICHT aus Repo!)
os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def render():
    st.header("💬 Chat mit Llama")

    # Chat-Verlauf in Session halten
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hallo 👋, wie kann ich dir helfen?"}
        ]

    # Verlauf anzeigen
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Eingabefeld
    if prompt := st.chat_input("Nachricht eingeben..."):
        # Nutzer-Eingabe anzeigen
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Modell-Antwort holen
        with st.chat_message("assistant"):
            with st.spinner("Lade Antwort..."):
                response = generate_llama_response(st.session_state.chat_messages)
                st.markdown(response)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})

    # Reset-Button für Verlauf
    if st.button("🔄 Chat zurücksetzen"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat zurückgesetzt. Wie kann ich dir helfen?"}
        ]
        st.experimental_rerun()


def generate_llama_response(history):
    # Prompt aus bisherigen Nachrichten bauen
    dialogue = ""
    for msg in history:
        if msg["role"] == "user":
            dialogue += f"User: {msg['content']}\n"
        else:
            dialogue += f"Assistant: {msg['content']}\n"

    prompt = dialogue + "Assistant:"

    # Replicate Call
    output = replicate.run(
        "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
        input={
            "prompt": prompt,
            "temperature": 0.6,
            "top_p": 0.9,
            "max_length": 512,
            "repetition_penalty": 1
        }
    )
    return "".join(output)
