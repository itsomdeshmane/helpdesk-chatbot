from fastapi import APIRouter, UploadFile, Form, BackgroundTasks
from ingestion.pdf_reader import extract_pdf_text
from ingestion.docx_reader import extract_docx_text
from ingestion.excel_reader import extract_excel_text
from ingestion.txt_reader import extract_txt_text
from ingestion.chunker import chunk_text
from llm.rag import embed_chunks
from ingestion.docs_loader import reload_docs, reload_markdown_docs
import asyncio

router = APIRouter(tags=["Documents"])

async def process_document_async(file_content: bytes, filename: str, tenant_id: str):
    """Process document in async manner to avoid blocking"""
    def extract_text():
        import io
        file_obj = io.BytesIO(file_content)
        
        if filename.endswith(".pdf"):
            return extract_pdf_text(file_obj)
        elif filename.endswith(".docx"):
            return extract_docx_text(file_obj)
        elif filename.endswith(".xlsx"):
            return extract_excel_text(file_obj)
        elif filename.endswith(".txt"):
            return extract_txt_text(file_obj)
        return ""
    
    # Run heavy extraction in thread pool
    content = await asyncio.to_thread(extract_text)
    
    if content:
        # Run chunking in thread pool
        chunks = await asyncio.to_thread(chunk_text, content)
        # Run embedding in thread pool
        await asyncio.to_thread(embed_chunks, chunks, tenant_id, filename)
        return len(chunks)
    return 0

@router.post("/upload", summary="Upload a document")
async def upload_document(file: UploadFile, tenant_id: str = Form("default")):
    """Upload and process document asynchronously to avoid blocking the server"""
    
    # Validate file type first
    if not any(file.filename.endswith(ext) for ext in [".pdf", ".docx", ".xlsx", ".txt"]):
        return {"error": "Unsupported format. Supported: PDF, DOCX, XLSX, TXT"}
    
    # Read file content
    file_content = await file.read()
    
    # Process document asynchronously (non-blocking)
    try:
        chunk_count = await process_document_async(file_content, file.filename, tenant_id)
        return {
            "status": "indexed",
            "filename": file.filename,
            "chunks": chunk_count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to process document: {str(e)}"
        }

@router.post("/reload", summary="Reload all documents")
async def reload_documents(background_tasks: BackgroundTasks, tenant_id: str = Form("default")):
    """
    Reload all documentation files from the docs folder in background.
    Non-blocking - returns immediately while docs load in background.
    """
    try:
        # Run reload in background to avoid blocking
        background_tasks.add_task(reload_docs, tenant_id=tenant_id)
        return {
            "status": "processing",
            "message": "Documentation reload started in background"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/reload-markdown", summary="Reload markdown documentation")
async def reload_markdown_documentation(background_tasks: BackgroundTasks, tenant_id: str = Form("default")):
    """
    Reload all markdown documentation with structure-aware chunking.
    This ensures lists, permissions, and hierarchical content stay together.
    Non-blocking - returns immediately while docs load in background.
    """
    try:
        # Run reload in background to avoid blocking
        background_tasks.add_task(reload_markdown_docs, tenant_id=tenant_id)
        return {
            "status": "processing",
            "message": "Markdown documentation reload started in background"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}