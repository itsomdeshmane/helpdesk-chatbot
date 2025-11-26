from docx import Document
from io import BytesIO

def extract_docx_text(file):
    """Extract text from a DOCX file."""
    try:
        # Read file content
        content = file.read()
        
        # Use python-docx to extract text
        doc = Document(BytesIO(content))
        text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return "\n".join(text)
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""