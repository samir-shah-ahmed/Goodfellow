from pypdf import PdfReader

def read_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        print(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    read_pdf("test_disclosure.pdf")
