# utils/result_card.py

import streamlit as st
import re
from sklearn.metrics.pairwise import cosine_similarity

# Neue Funktion: semantisches Highlighting

def highlight_semantic_terms(text, query, embedding_model, threshold=0.7):
    STOPWORDS = {
        "ein", "eine", "einer", "der", "die", "das", "und", "oder", "für", "mit", "in",
        "auf", "von", "zu", "zur", "vom", "den", "des", "am", "im", "aus", "an", "dem",
        "ist", "es", "sind", "dass", "welche", "das", "dies", "diese", "dieser", "dieses",
        "etc", "sofern", "wenn", "wie", "auch"
    }

    words = list(set(re.findall(r'\b\w{4,}\b', text)))
    words_filtered = [w for w in words if w.lower() not in STOPWORDS]

    if not words_filtered:
        return text

    query_embedding = embedding_model.embed_query(query)
    word_embeddings = embedding_model.client.encode(words_filtered)

    similarities = cosine_similarity([query_embedding], word_embeddings)[0]

    for word, sim in zip(words_filtered, similarities):
        if sim >= threshold:
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
            text = pattern.sub(f"<mark>{word}</mark>", text)

    return text


def render_result_card(doc, idx, query):
    """
    Zeigt den Textabschnitt als Karte an, markiert Suchbegriffe und gibt Snippet zurück.
    """
    # Snippet (erste 500 Zeichen)
    snippet = str(doc.page_content[:500])
    if len(doc.page_content) > 500:
        snippet += "…"

    # Suchbegriffe hervorheben (case-insensitive)
    for term in query.split():
        snippet = re.sub(f"(?i){re.escape(term)}", f"**{term}**", snippet)

    # Überschrift anzeigen
    st.markdown(f"### Treffer {idx+1}: {doc.metadata.get('heading', '')}")
    
    # Snippet anzeigen
    st.markdown(snippet)
    
    # Snippet zurückgeben (optional, falls du es später weiterverarbeiten willst)
    return snippet
