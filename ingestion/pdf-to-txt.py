from pypdf import PdfReader
import os

reader = PdfReader("data\Employee-Handbook.pdf")
txt_path = "data\employee_handbook.txt"

full_text = ""

for page in reader.pages[2:]:
    text = page.extract_text()
    if text:
        full_text += text + "\n"

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(full_text)