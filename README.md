# PDF Research Paper Summarizer

A desktop tool that turns research-paper PDFs into short **abstractive summaries** with a transformer model (BART). It extracts text from the PDF, falls back to **OCR** when the extracted text looks broken, cleans and chunks the text, summarizes it, and shows the result in a simple GUI.

> NLP course project, 2025, Université Française d'Égypte (Computer Engineering), supervised by Prof. Ahmed Magdy. Built by Youssef ALY and Yassin Elwakil.

<!-- Add a screenshot of the GUI as images/gui.png, then uncomment the next line:
![GUI screenshot](images/gui.png)
-->

## Features

- **Text extraction** with [pdfplumber](https://github.com/jsvine/pdfplumber), with an automatic fallback to **Tesseract OCR** (300 DPI) when the text looks broken.
- **Text repair:** rejoins hyphenated line breaks, adds missing spaces after punctuation and splits stuck words.
- **Sentence-aware chunking** with NLTK, so long papers fit the model's input limit without cutting sentences in half.
- **Abstractive summarization** with `facebook/bart-large-cnn` (beam search, length penalty and no-repeat n-grams for readable, non-repetitive output).
- **Tkinter GUI:** pick a PDF, generate the summary, save it as a `.txt` file. A command-line mode is also available.
- Runs on a **GPU (CUDA)** when available, otherwise on the CPU.

## How it works

```
PDF ──► pdfplumber text extraction
          │
          ├─ text looks broken? ──► Tesseract OCR (pdf2image, 300 DPI)
          ▼
     text repair and cleaning
          ▼
     sentence-aware chunks (~3,000 characters)
          ▼
     BART summary of each chunk
          ▼
     combined summaries ──► BART second pass ──► final summary
```

| Step | Details |
|---|---|
| Quality check | OCR is used when the text is very short, has stuck words, has words that look run together, or contains hyphenated line breaks |
| Chunk summaries | `facebook/bart-large-cnn`, 8 beams, `no_repeat_ngram_size=3`, `length_penalty=1.2`, 150 to 350 tokens per chunk |
| Final summary | The chunk summaries are joined and summarized again (180 to 400 tokens) |

## Quick start

**Requirements**

- Python 3.10 or newer (developed on 3.13)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), available on your `PATH`
- [Poppler](https://poppler.freedesktop.org/), needed by `pdf2image` (on Windows, add its `bin` folder to your `PATH`)
- About 1.6 GB of disk space: the BART model is downloaded automatically on the first run

**Install**

```bash
git clone https://github.com/<your-username>/pdf-research-paper-summarizer.git
cd pdf-research-paper-summarizer

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

For GPU support, install PyTorch with the command from [pytorch.org](https://pytorch.org/get-started/locally/) first.

**Run the GUI**

```bash
python src/gui.py
```

**Run from the command line**

```bash
python src/main.py path/to/paper.pdf
```

The model loads when the program starts, so the window can take a moment to appear.

## Evaluation

The tool was tested on **20 academic PDFs** (1 to 15 pages) from computer science, engineering and social sciences. Summaries were judged **qualitatively** on coherence, coverage and readability.

- Text extraction worked on all 20 documents; OCR was needed on about 30% of them.
- Summary generation took roughly 2 to 12 minutes per paper, depending on length.
- Example: a 3,500-word paper became a summary of about 400 words that kept the main contributions, methods and conclusions.

No quantitative metrics (such as ROUGE) were computed.

## Known limitations

- **Aggressive OCR trigger.** The `needs_ocr()` rule treats any word of 10 or more lowercase letters as a sign of broken text, so OCR can run even on clean PDFs and slow things down. The thresholds in `src/main.py` can be tightened.
- **Long papers lose detail in the final pass.** The second summarization step truncates its input at 1,024 tokens, so with many chunks the later parts of a paper can be under-represented.
- **News-trained model.** `bart-large-cnn` is fine-tuned on news articles, not scientific text, so summaries can read like news and may include inaccuracies.
- **English only, text only.** OCR runs in English, and figures, tables and equations are not handled.
- **GUI freezes while working.** Summarization runs on the main thread, and progress messages are printed to the console, not the window.

## Future work

- Fine-tune the summarizer on scientific corpora.
- Summarize hierarchically so that long papers are covered evenly.
- Run summarization in a background thread with a progress bar.
- Handle figures, tables and equations; add multilingual support.
- Evaluate with ROUGE and human ratings.

## Project structure

```
pdf-research-paper-summarizer/
├── src/
│   ├── main.py          # extraction, OCR, cleaning, chunking, summarization (also a CLI)
│   └── gui.py           # Tkinter interface
├── assets/
│   └── logo.png
├── requirements.txt
└── README.md
```

## Authors

- **Youssef ALY**, M2 Data, Knowledge and Hybrid Artificial Intelligence, Université Paris-Saclay
- **Yassin Elwakil**

## Acknowledgements

Prof. Ahmed Magdy for supervision. Built with [Hugging Face Transformers](https://github.com/huggingface/transformers), [BART](https://arxiv.org/abs/1910.13461), [pdfplumber](https://github.com/jsvine/pdfplumber), [Tesseract](https://github.com/tesseract-ocr/tesseract) and [NLTK](https://www.nltk.org/).
