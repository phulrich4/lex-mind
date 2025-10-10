# tabs/chat_tab.py
import streamlit as st
import requests
import time

# -------------------------------
# Hugging Face API Call
# -------------------------------
def generate_hf_response(messages):
    HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]
    MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

    # Prompt aus bisherigen Nachrichten zusammenbauen
    dialogue = ""
    for m in messages:
        dialogue += f"{m['role'].capitalize()}: {m['content']}\n"
    dialogue += "Assistant:"

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": dialogue,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 400,
            "return_full_text": False
        }
    }

    # Retry-Mechanismus (HF ist manchmal kurz ausgelastet)
    for attempt in range(3):
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL}",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            else:
                return str(data)
        elif response.status_code == 503:
            # Modell lädt noch (kommt häufig bei HF)
            st.info("🚀 Modell wird geladen – bitte kurz warten...")
            time.sleep(10)
        else:
            st.error(f"Fehler {response.status_code}: {response.text}")
            break

    return "⚠️ Das Modell ist aktuell nicht erreichbar. Bitte versuche es in ein paar Sekunden erneut."


# -------------------------------
# Chat Interface
# -------------------------------
def render():
    st.subheader("💬 Chat mit LexMind (Mistral 7B über Hugging Face)")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Chatverlauf anzeigen
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Neue Nutzereingabe
    if prompt := st.chat_input("Frage stellen oder mit der KI chatten..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Antwort generieren
        with st.chat_message("assistant"):
            with st.spinner("Mistral denkt nach..."):
                answer = generate_hf_response(st.session_state.chat_messages)
                st.markdown(answer)

        # Antwort speichern
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})

    # Verlauf löschen
    if st.button("🔄 Chatverlauf löschen"):
        st.session_state.chat_messages = []
        st.rerun()
