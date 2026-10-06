from pathlib import Path
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from main import summarize_pdf


# colors

BG_MAIN = "#fef7f2"       
BG_CARD = "#fef7f2"        
ACCENT = "#050B70"         
TEXT_COLOR = "#0A0965" 
BTN_GREEN = "#7D161B"
BTN_BLUE = "#050B70"


# Root Window

root = tk.Tk()
root.title("Research Paper Summarizer")
root.geometry("1000x720")
root.configure(bg=BG_MAIN)


# Top Header

header = tk.Frame(root, bg=BG_MAIN)
header.pack(fill=tk.X, pady=15, padx=20)

title_label = tk.Label(
    header,
    text="Research Paper Summarizer",
    font=("Segoe UI", 22, "bold"),
    fg=TEXT_COLOR,
    bg=BG_MAIN
)
title_label.pack(side=tk.LEFT)

subtitle = tk.Label(
    header,
    text="NLP Project By Y² (Youssef & Yassin)",
    font=("Segoe UI", 11),
    fg="#050B70",
    bg=BG_MAIN
)
subtitle.pack(side=tk.LEFT, padx=15)

# Logo
logo_frame = tk.Frame(header, bg=BG_MAIN)
logo_frame.pack(side=tk.RIGHT)

# Load larger logo
logo_img = tk.PhotoImage(file=str(Path(__file__).resolve().parent.parent / "assets" / "logo.png"))

logo_label = tk.Label(
    logo_frame,
    image=logo_img,
    bg=BG_MAIN
)
logo_label.pack()

# Card Container
card = tk.Frame(root, bg=BG_CARD)
card.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)


# PDF Selection

pdf_path_var = tk.StringVar()
PLACEHOLDER_TEXT = " Select your PDF file to Summarize"

def browse_pdf():
    file_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        pdf_path_var.set(file_path)
        pdf_entry.config(fg=TEXT_COLOR)

pdf_frame = tk.Frame(card, bg=BG_CARD)
pdf_frame.pack(fill=tk.X, pady=15)

entry_border = tk.Frame(
    pdf_frame,
    bg="#050B70",
    padx=2,
    pady=2
)
entry_border.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

pdf_entry = tk.Entry(
    entry_border,
    textvariable=pdf_path_var,
    font=("Segoe UI", 11),
    bg="#fef7f2",
    fg="#888888",                 
    insertbackground=TEXT_COLOR,
    relief="flat"
)
pdf_entry.pack(fill=tk.X, ipady=6)

def on_entry_focus_in(event):
    if pdf_path_var.get() == PLACEHOLDER_TEXT:
        pdf_entry.delete(0, tk.END)
        pdf_entry.config(fg=TEXT_COLOR)

def on_entry_focus_out(event):
    if not pdf_path_var.get():
        pdf_entry.insert(0, PLACEHOLDER_TEXT)
        pdf_entry.config(fg="#888888")

pdf_entry.bind("<FocusIn>", on_entry_focus_in)
pdf_entry.bind("<FocusOut>", on_entry_focus_out)

# Set initial placeholder
pdf_entry.insert(0, PLACEHOLDER_TEXT)

browse_btn = tk.Button(
    pdf_frame,
    text="Browse PDF",
    command=browse_pdf,
    bg=ACCENT,
    fg="white",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=15,
    pady=6
)
browse_btn.pack(side=tk.RIGHT)



# Output Box


output_border = tk.Frame(
    card,
    bg="#050B70",    
    padx=2,
    pady=2
)
output_border.pack(fill=tk.BOTH, expand=True, pady=15)

output_box = scrolledtext.ScrolledText(
    output_border,
    wrap=tk.WORD,
    font=("Segoe UI", 11),
    bg="#fef7f2",
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    relief="flat",
    height=20
)
output_box.pack(fill=tk.BOTH, expand=True)



# Buttons

btn_frame = tk.Frame(card, bg=BG_CARD)
btn_frame.pack(pady=10)

def run_summary():
    path = pdf_path_var.get().strip()
    if not path:
        messagebox.showerror("Error", "Please select a PDF file first.")
        return

    output_box.delete("1.0", tk.END)
    output_box.insert(
        tk.END,
        "⏳ Extracting text, running OCR if needed, and generating summary...\n\n"
    )
    root.update()

    try:
        summary = summarize_pdf(path)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, summary)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_summary():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "No summary to save.")
        return

    file = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text File", "*.txt")]
    )
    if file:
        with open(file, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", "Summary saved successfully!")

generate_btn = tk.Button(
    btn_frame,
    text="Generate Summary",
    command=run_summary,
    bg=BTN_GREEN,
    fg="white",
    font=("Segoe UI", 12, "bold"),
    relief="flat",
    padx=25,
    pady=10
)
generate_btn.pack(side=tk.LEFT, padx=10)

save_btn = tk.Button(
    btn_frame,
    text="Save Summary",
    command=save_summary,
    bg=BTN_BLUE,
    fg="white",
    font=("Segoe UI", 12, "bold"),
    relief="flat",
    padx=25,
    pady=10
)
save_btn.pack(side=tk.LEFT, padx=10)


# Footer
footer = tk.Label(
    root,
    text="Y² Project • Youssef & Yassin • NLP Research Tool",
    font=("Segoe UI", 9),
    fg="#9FB6CD",
    bg=BG_MAIN
)
footer.pack(pady=10)

root.mainloop()
