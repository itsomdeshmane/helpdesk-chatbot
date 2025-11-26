"""
Simple text file reader for documentation.
"""

def extract_txt_text(file_obj):
    """
    Extract text from a plain text file.
    
    Args:
        file_obj: File object (opened in binary mode)
    
    Returns:
        str: Extracted text content
    """
    try:
        # Read and decode the text
        content = file_obj.read()
        
        # Try UTF-8 first, fallback to latin-1 if that fails
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1', errors='ignore')
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading text file: {str(e)}")






