import openpyxl
from io import BytesIO

def extract_excel_text(file):
    """Extract text from an Excel file."""
    try:
        # Read file content
        content = file.read()
        
        # Use openpyxl to extract text
        workbook = openpyxl.load_workbook(BytesIO(content))
        text = []
        
        for sheet in workbook.worksheets:
            text.append(f"Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                row_text = "\t".join([str(cell) if cell is not None else "" for cell in row])
                if row_text.strip():
                    text.append(row_text)
        
        return "\n".join(text)
    except Exception as e:
        print(f"Error extracting Excel text: {e}")
        return ""