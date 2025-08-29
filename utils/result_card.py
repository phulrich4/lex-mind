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
    Zeigt einen Suchtreffer im Karten-Design inkl. Download an.
    """
    title = doc.metadata.get("heading", doc.metadata.get("source", f"Treffer {idx+1}"))
    category = doc.metadata.get("category", "–")
    year = doc.metadata.get("year", "–")
    snippet = doc.page_content[:250] + ("…" if len(doc.page_content) > 250 else "")

    # Hervorhebung
    snippet = highlight_terms(snippet, query)

    file_path = doc.metadata.get("source")
    file_name = os.path.basename(file_path) if file_path else "Dokument"

    with st.container():
        st.markdown("---")  # Trennlinie zwischen Treffern
        st.markdown(f"### {title}")

        # Badges
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(
                f"<span style='background-color:#E5E7EB; padding:3px 8px; border-radius:8px;'>{category}</span>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<span style='background-color:#F87171; padding:3px 8px; border-radius:8px;'>PDF</span>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<span style='background-color:#BFDBFE; padding:3px 8px; border-radius:8px;'>{year}</span>",
                unsafe_allow_html=True
            )

        # Snippet
        st.markdown(f"<p style='color:#374151;'>{snippet}</p>", unsafe_allow_html=True)

        # Download-Button falls Datei vorhanden
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📥 {file_name} herunterladen",
                    data=f,
                    file_name=file_name,
                    mime="application/pdf"
                )
