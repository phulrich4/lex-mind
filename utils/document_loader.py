# utils/document_loader.py
import os
import fitz  # PyMuPDF
import docx
import re
from langchain.docstore.document import Document
from utils.category_manager import assign_category
from docx import Document as DocxDocument
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Funktion: Text in strukturierte Abschnitte (Chunks) teilen
def split_into_chunks_by_heading(text):
    pattern = r"(?=^\s*(§{1,2}\s*\d+[^\n]*|Art\.?\s*\d+[^\n]*|Ziff\.?\s*\d+[^\n]*|Artikel\s+\d+[^\n]*))"
    chunks = re.split(pattern, text, flags=re.MULTILINE)

    grouped = []
    for i in range(0, len(chunks) - 1, 2):
        heading = chunks[i].strip()
        content = chunks[i + 1].strip()
        grouped.append({"heading": heading, "content": content})

    if len(chunks) % 2 == 1:
        grouped.append({"heading": "–", "content": chunks[-1].strip()})
    return grouped

# PDF-Dateien laden und in Chunks aufteilen
def extract_chunks_from_pdf(path):
    doc = fitz.open(path)
    all_chunks = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        page_chunks = split_into_chunks_by_heading(text)
        for chunk in page_chunks:
            all_chunks.append(Document(
                page_content=chunk["content"],
                metadata={
                    "source": os.path.basename(path),
                    "page": i,
                    "heading": chunk["heading"]
                }
            ))
    return all_chunks

# DOCX-Dateien laden und in Chunks aufteilen
def extract_chunks_from_docx(path):
    doc = docx.Document(path)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    chunks = split_into_chunks_by_heading(full_text)
    all_chunks = []
    for chunk in chunks:
        all_chunks.append(Document(
            page_content=chunk["content"],
            metadata={
                "source": os.path.basename(path),
                "page": None,
                "heading": chunk["heading"]
            }
        ))
    return all_chunks

# Lade alle Dokumente im Ordner und weise Metadaten zu
def load_documents_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[-1].lower()

        if ext == ".pdf":
            chunks = extract_chunks_from_pdf(full_path)
            # Optional: Vorschau übernehmen
            # shutil.copy(full_path, "previews")  # falls du PDF direkt nutzen willst

        elif ext == ".docx":
            chunks = extract_chunks_from_docx(full_path)
            export_docx_to_pdf(full_path)  # Vorschau erstellen

        else:
            continue

        # Kategorie zuweisen und Metadaten ergänzen
        for chunk in chunks:
            category = assign_category(chunk.page_content)
            chunk.metadata["category"] = category
            documents.append(chunk)

    return documents

# DOCX zu PDF exportieren (Vorschau)
def export_docx_to_pdf(docx_path, output_dir="previews"):
    os.makedirs(output_dir, exist_ok=True)
    doc = DocxDocument(docx_path)
    pdf_path = os.path.join(output_dir, os.path.basename(docx_path).replace(".docx", ".pdf"))

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 40

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            y -= 15
            continue

        for line in text.split("\n"):
            c.drawString(40, y, line[:120])
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 40

    c.save()
    return pdf_path

