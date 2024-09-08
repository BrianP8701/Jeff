import os
import markdown
import PyPDF2
import pytesseract
from PIL import Image
import io
import hashlib
from server.embeddings.embed import get_embedding, chunk_content
from server.database.queries import create_file, get_file_by_content_hash
from server.constants import folder_path
import traceback

def get_file_contents(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() in ['.md', '.txt']:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if ext.lower() == '.md':
                content = markdown.markdown(content)
            return content
    elif ext.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    
    if not text.strip():  # If no text was extracted, use OCR
        return ocr_pdf(file_path)
    
    # Remove NUL characters
    return text.replace('\x00', '')

def ocr_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        for page in range(len(pdf.pages)):
            page_obj = pdf.pages[page]
            for image in page_obj.images:
                img = Image.open(io.BytesIO(image.data))
                text += pytesseract.image_to_string(img)
    
    # Remove NUL characters
    return text.replace('\x00', '')

def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def process_files(folder_path: str):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            if ext.lower() in ['.md', '.txt', '.pdf']:
                try:
                    content = get_file_contents(file_path)
                    chunks = chunk_content(content)
                    
                    for i, chunk in enumerate(chunks):
                        content_hash = get_content_hash(chunk)
                        existing_file = get_file_by_content_hash(content_hash)
                        if existing_file:
                            continue

                        embedding = get_embedding(chunk)
                        
                        file_data = {
                            "name": f"{file}_chunk_{i+1}",
                            "path": os.path.abspath(file_path),  # Use absolute path
                            "content": chunk,
                            "content_hash": content_hash,
                            "embedding": embedding
                        }
                        
                        stored_file = create_file(file_data)
                        print(f"Stored file chunk: {stored_file.id} - {stored_file.name}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    print(traceback.format_exc())  # This will print the full stack trace

if __name__ == "__main__":
    folder_path = folder_path
    process_files(folder_path)
