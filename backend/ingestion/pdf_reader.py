import pdfplumber
from io import BytesIO

def extract_pdf_text(file):
    """Extract text from a PDF file. Optimized to avoid blocking."""
    try:
        text_parts = []
        
        # Read file content once
        content = file.read()
        
        # Use pdfplumber with minimal settings for speed
        with pdfplumber.open(BytesIO(content)) as pdf:
            # Limit to first 100 pages to avoid extremely long processing
            max_pages = min(len(pdf.pages), 100)
            
            for i in range(max_pages):
                try:
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as page_error:
                    print(f"   Warning: Could not extract page {i+1}: {page_error}")
                    continue
        
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""