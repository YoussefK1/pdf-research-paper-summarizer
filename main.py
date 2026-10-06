import pdfplumber
import re
import nltk
import pytesseract
import torch
from pdf2image import convert_from_path
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Model
MODEL_NAME = "facebook/bart-large-cnn"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[INFO] Loading summarization model on {device} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# 1. PDF Extraction (PDFPlumber)
def extract_text_pdfplumber(pdf_path):
    text_pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    text_pages.append(t)
    except Exception as e:
        print("[WARN] pdfplumber failed:", e)
        return ""

    return "\n".join(text_pages)

# 2. OCR Extraction 

def extract_text_ocr(pdf_path):
    print("[INFO] Running OCR extraction (high quality)...")
    pages = convert_from_path(pdf_path, dpi=300)

    text = ""
    for img in pages:
        page_text = pytesseract.image_to_string(img, lang="eng")
        text += page_text + "\n"

    return text


# 3. Text Quality Check
# Determines if the pdfplumber text is too broken sp switch to OCR

def needs_ocr(text):
    if len(text.strip()) < 500:
        return True

    # Check stuck words: "securelystored"
    if re.search(r"[a-z]{4,}[A-Z]{1}[a-z]+", text):
        return True

    # Too many missing spaces
    if re.search(r"[a-z]{10,}", text):
        return True

    # Hyphenated breaks like "re-\ncognition"
    if re.search(r"[a-zA-Z]-\s*\n\s*[a-zA-Z]", text):
        return True

    return False



# 4. Repair broken words
def repair_broken_words(text):
    # Join hyphenated line breaks: "real-\ntime" → "real time"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Fix missing spaces after periods
    text = re.sub(r"\.([A-Za-z])", r". \1", text)

    # Break stuck words: lowercase+uppercase
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # Add missing spaces after commas
    text = re.sub(r",([A-Za-z])", r", \1", text)

    return text


# 5. Light cleaning (keep sentence integrity)
def clean_text(text):
    text = repair_broken_words(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text



# 6. Sentence-aware chunking

def chunk_text(text, max_len=2500):
    sents = sent_tokenize(text)
    chunks = []
    current = ""

    for s in sents:
        if len(current) + len(s) < max_len:
            current += " " + s
        else:
            chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())

    return chunks



# 7. Summarization of chunks and final summarization

def summarize_chunks(chunks):
    summaries = []

    for i, chunk in enumerate(chunks, 1):
        print(f"[INFO] Summarizing chunk {i}/{len(chunks)} ...")

        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(device)

        out = model.generate(
            **inputs,
            max_length=350,
            min_length=150,
            num_beams=8,
            no_repeat_ngram_size=3,
            length_penalty=1.2,
            early_stopping=True
        )

        summary = tokenizer.decode(out[0], skip_special_tokens=True)
        summaries.append(summary)

    # Combine and compress final summary
    combined = " ".join(summaries)
    final_inputs = tokenizer(
        combined,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(device)

    final_out = model.generate(
        **final_inputs,
        max_length=400,
        min_length=180,
        num_beams=8,
        no_repeat_ngram_size=3,
        length_penalty=1.2,
        early_stopping=True
    )

    return tokenizer.decode(final_out[0], skip_special_tokens=True)


# 8. FULL PIPELINE
def summarize_pdf(pdf_path):
    print("[INFO] Extracting text using pdfplumber...")
    raw = extract_text_pdfplumber(pdf_path)

    # Check quality
    if needs_ocr(raw):
        print("[WARN] PDF text is low quality → switching to OCR...")
        raw = extract_text_ocr(pdf_path)

    # Clean
    raw = clean_text(raw)

    if len(raw) < 200:
        return "Error: Could not extract enough text."

    chunks = chunk_text(raw, max_len=3000)

    print(f"[INFO] Total chunks: {len(chunks)}")
    summary = summarize_chunks(chunks)
    return summary


# 9. Command-line execution
if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1]
    print("\n FINAL SUMMARY \n")
    print(summarize_pdf(pdf_path))
