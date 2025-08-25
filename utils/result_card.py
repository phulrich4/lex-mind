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


def render_result_card(doc, index, query, embeddings):
    """
    Zeigt ein Suchergebnis mit Metadaten, Textauszug und Vorschau-Button an.
    """
    st.markdown(f"### Treffer {index + 1}")

    content = doc.page_content
    source = doc.metadata.get("source", "unbekannt")
    page = doc.metadata.get("page", "-")
    heading = doc.metadata.get("heading", "-")
    category = doc.metadata.get("category", "Andere")

    st.markdown(f"**📂 Kategorie:** `{category}`")
    st.markdown(f"**📄 Dokument:** `{source}`")
    st.markdown(f"**📌 Abschnitt:** *{heading}*  &nbsp;&nbsp;|&nbsp;&nbsp;  **🗂️ Seite:** {page}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(content, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"🔍 Vorschau anzeigen (Treffer {index + 1})"):
            preview_path = os.path.join("previews", source.replace(".docx", ".pdf"))
            if os.path.exists(preview_path):
                st.markdown(f"[📄 PDF-Vorschau öffnen]({preview_path})", unsafe_allow_html=True)
            else:
                st.warning("Keine Vorschau verfügbar.")

    with col2:
        if st.button(f"Hervorheben im Original (Treffer {index + 1})"):
            from utils.highlighter import DocumentHighlighter
            doc_path = os.path.join("docs", source)
            if os.path.exists(doc_path):
                highlighter = DocumentHighlighter(doc_path)
                output_path = highlighter.highlight(content)
                st.success(f"Gespeichert unter: {output_path}")
            else:
                st.warning(f"Dokument nicht gefunden: {source}")
