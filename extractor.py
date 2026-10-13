import io
import re
import pdfplumber
import docx

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_document_text(filename: str, file_bytes: bytes) -> str:
    lower_name = filename.lower()
    full_text = ""
    
    try:
        if lower_name.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                full_text = " ".join([page.extract_text() or "" for page in pdf.pages])
        elif lower_name.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = " ".join([p.text for p in doc.paragraphs if p.text])
        elif lower_name.endswith(".txt"):
            full_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        raise ValueError(f"Corrupted file format: {str(e)}")

    cleaned = clean_text(full_text)
    
    # Catch image-based PDFs
    if len(cleaned) < 50:
        raise ValueError("Insufficient text detected. If this is a PDF, ensure it is text-based and not a scanned image.")
        
    return cleaned