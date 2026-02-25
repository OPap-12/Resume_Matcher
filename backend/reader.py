from pypdf import PdfReader

def extract_resume_text(pdf_path):
    # 1. Initialize the Reader with your file
    reader = PdfReader(pdf_path)
    
    # 2. Extract text from ALL pages and combine them
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
        
    return full_text

# TEST IT: Put a sample PDF in your folder and name it 'my_resume.pdf'
if __name__ == "__main__":
    resume_path = "my_resume.pdf"
    content = extract_resume_text(resume_path)
    print("--- EXTRACTED TEXT ---")
    print(content)