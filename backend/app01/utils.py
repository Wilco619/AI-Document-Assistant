import docx
import PyPDF2
import io
from typing import Tuple

class DocumentConverter:
    @staticmethod
    def extract_text(file) -> Tuple[str, str]:
        #Extract text from various file formats
        filename = file.name.lower()
        content = ""
        
        if filename.endswith('.txt'):
            content = file.read().decode('utf-8')
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            content = "\n".join([page.extract_text() for page in pdf_reader.pages])
        
        return content, filename
    