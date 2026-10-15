from pypdf import PdfReader
import os

input_folder = r"D:\exampdfs"
output_folder = r"D:\exampdfs\extracted_text"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):
        path = os.path.join(input_folder, filename)
        try:
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            out_name = os.path.splitext(filename)[0] + ".txt"
            out_path = os.path.join(output_folder, out_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Done: {filename} -> {out_name}")
        except Exception as e:
            print(f"Failed: {filename} ({e})")

print("All done.")