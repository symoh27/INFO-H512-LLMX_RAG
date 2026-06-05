import pypdf

def extract(pdf_path, txt_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        with open(txt_path, 'w', encoding='utf-8') as f:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    f.write(text + "\n")
        print(f"Extracted {pdf_path} to {txt_path}")
    except Exception as e:
        print(f"Failed extracting {pdf_path}: {e}")

extract(r"C:\Users\symoh\cloud-computing\notebook-tester\notebook-scripts\SHapRAG\facile.pdf", "facile_extracted.txt")
extract(r"C:\Users\symoh\cloud-computing\notebook-tester\notebook-scripts\SHapRAG\INFO-H512-Project.pdf", "INFO-H512-Project_extracted.txt")
