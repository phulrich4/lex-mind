# tabs/chat_tab.py
import streamlit as st
# from utils.search_llm import run_llm_search

def render():
    st.header("💬 Chat – GPT4All Mini Suche")
"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Frage eingeben...")

    if user_input:
        st.chat_message("user").write(user_input)

        answer = run_llm_search(user_input)

        st.chat_message("assistant").write(answer)

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
"""
