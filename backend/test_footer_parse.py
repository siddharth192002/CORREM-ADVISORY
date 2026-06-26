import pdfplumber
import os

pdf_path = r"C:\Users\siddh\Downloads\HDFC BANK.pdf"
if not os.path.exists(pdf_path):
    print("PDF not found!")
    exit(1)

with pdfplumber.open(pdf_path) as pdf:
    # Page 3
    page = pdf.pages[2]
    words = page.extract_words()
    
    # Group words by top
    lines_words = {}
    for w in words:
        top_rounded = round(w["top"], 1)
        found = False
        for t in lines_words:
            if abs(t - w["top"]) <= 3:
                lines_words[t].append(w)
                found = True
                break
        if not found:
            lines_words[w["top"]] = [w]
            
    # Print lines below top=650
    print("=== LINES BELOW TOP 650 ===")
    for t in sorted(lines_words.keys()):
        if t > 650:
            line_words = sorted(lines_words[t], key=lambda w: w["x0"])
            line_str = " ".join([w["text"] for w in line_words])
            print(f"Top: {t:.2f} | {line_str}")
            for w in line_words:
                print(f"  Word: '{w['text']}' at x0={w['x0']:.1f}, x1={w['x1']:.1f}")
