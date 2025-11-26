"""
Auto-load documentation files from the docs folder on startup.
Supports PDF, DOCX, XLSX, TXT, and MD files.
"""
import os
import time
from pathlib import Path
from ingestion.pdf_reader import extract_pdf_text
from ingestion.docx_reader import extract_docx_text
from ingestion.excel_reader import extract_excel_text
from ingestion.txt_reader import extract_txt_text
from ingestion.chunker import chunk_text
from ingestion.markdown_chunker import chunk_markdown
from llm.rag import embed_chunks, clear_chunks_by_filename

def load_docs_from_folder(docs_folder: str = None, tenant_id: str = "default", module: str = "general"):
    """
    Load and process all documentation files from the docs folder.
    
    Args:
        docs_folder: Path to the docs folder (defaults to ../docs from backend)
        tenant_id: Tenant ID for the embeddings
        module: Module name for categorization
    """
    if docs_folder is None:
        # Default to docs folder in project root
        backend_dir = Path(__file__).parent.parent
        docs_folder = backend_dir.parent / "docs"
    else:
        docs_folder = Path(docs_folder)
    
    if not docs_folder.exists():
        print(f"Docs folder not found: {docs_folder}")
        print("Creating docs folder...")
        docs_folder.mkdir(parents=True, exist_ok=True)
        print(f"Please place your documentation files (PDF, DOCX, XLSX) in: {docs_folder}")
        return
    
    # Find all supported files
    supported_extensions = ['.pdf', '.docx', '.xlsx', '.txt']
    doc_files = []
    
    for ext in supported_extensions:
        doc_files.extend(docs_folder.glob(f"*{ext}"))
    
    if not doc_files:
        print(f"No documentation files found in {docs_folder}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return
    
    print(f"\n{'='*60}")
    print(f"Loading documentation files from: {docs_folder}")
    print(f"{'='*60}")
    
    total_chunks = 0
    processed_files = 0
    failed_files = []
    
    for file_path in doc_files:
        try:
            file_start = time.time()
            print(f"\n📄 Processing: {file_path.name}")
            print(f"   File type: {file_path.suffix.upper()}")
            print(f"   File size: {file_path.stat().st_size / 1024:.2f} KB")
            
            content = ""
            
            # Extract text based on file type
            print(f"   ⏳ Extracting text from {file_path.suffix} file...")
            extract_start = time.time()
            with open(file_path, 'rb') as f:
                if file_path.suffix == '.pdf':
                    content = extract_pdf_text(f)
                elif file_path.suffix == '.docx':
                    content = extract_docx_text(f)
                elif file_path.suffix == '.xlsx':
                    content = extract_excel_text(f)
                elif file_path.suffix == '.txt':
                    content = extract_txt_text(f)
            extract_time = time.time() - extract_start
            print(f"   ✅ Text extracted in {extract_time:.2f}s ({len(content)} characters)")
            
            if not content or len(content.strip()) < 10:
                print(f"   ⚠️  Warning: No content extracted from {file_path.name}")
                continue
            
            # Chunk the text
            print(f"   ⏳ Splitting into chunks...")
            chunk_start = time.time()
            chunks = chunk_text(content)
            chunk_time = time.time() - chunk_start
            print(f"   ✅ Created {len(chunks)} chunks in {chunk_time:.2f}s")
            
            # Clear old chunks for this file to prevent duplicates
            print(f"   🗑️  Clearing old chunks for: {file_path.name}")
            clear_chunks_by_filename(file_path.name, tenant_id)
            
            # Embed and store chunks
            print(f"   ⏳ Storing chunks...")
            embed_start = time.time()
            embed_chunks(chunks, module, tenant_id, file_path.name)
            embed_time = time.time() - embed_start
            print(f"   ✅ Chunks stored in {embed_time:.2f}s")
            
            total_chunks += len(chunks)
            processed_files += 1
            
            file_time = time.time() - file_start
            print(f"   ✅ Successfully indexed {file_path.name} (Total: {file_time:.2f}s)")
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path.name}: {str(e)}")
            failed_files.append((file_path.name, str(e)))
    
    print(f"\n{'='*60}")
    print(f"Documentation Loading Summary:")
    print(f"  • Files processed: {processed_files}/{len(doc_files)}")
    print(f"  • Total chunks indexed: {total_chunks}")
    if failed_files:
        print(f"  • Failed files: {len(failed_files)}")
        for filename, error in failed_files:
            print(f"    - {filename}: {error}")
    print(f"{'='*60}\n")

def reload_docs(tenant_id: str = "default", module: str = "general"):
    """
    Reload all documentation files from the docs folder.
    Useful for refreshing the knowledge base when docs are updated.
    """
    print("\n🔄 Reloading documentation files...")
    load_docs_from_folder(tenant_id=tenant_id, module=module)


def load_markdown_docs(markdown_file: str = None, tenant_id: str = "default", module: str = "codebase_docs"):
    """
    Load and process a markdown documentation file with structure-aware chunking.
    Preserves sections, headings, lists, and code blocks together for better context.
    
    Args:
        markdown_file: Path to the markdown documentation file (defaults to docs/VERAX_DOCUMENTATION.md)
        tenant_id: Tenant ID for the embeddings
        module: Module name for categorization (defaults to "codebase_docs")
    
    Returns:
        int: Number of chunks created and stored
    """
    if markdown_file is None:
        # Default to VERAX_DOCUMENTATION.md in docs folder
        backend_dir = Path(__file__).parent.parent
        markdown_file = backend_dir.parent / "docs" / "VERAX_DOCUMENTATION.md"
    else:
        markdown_file = Path(markdown_file)
    
    if not markdown_file.exists():
        print(f"❌ Markdown documentation file not found: {markdown_file}")
        return 0
    
    try:
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"Loading Markdown Documentation")
        print(f"{'='*60}")
        print(f"\n📄 Processing: {markdown_file.name}")
        print(f"   File size: {markdown_file.stat().st_size / 1024:.2f} KB")
        
        # Read markdown content
        print(f"   ⏳ Reading markdown file...")
        read_start = time.time()
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        read_time = time.time() - read_start
        print(f"   ✅ Content read in {read_time:.2f}s ({len(content)} characters)")
        
        if not content or len(content.strip()) < 10:
            print(f"   ⚠️  Warning: No content found in {markdown_file.name}")
            return 0
        
        # Clear old chunks for this file before loading new ones
        print(f"   🗑️  Clearing old chunks for: {markdown_file.name}")
        clear_chunks_by_filename(markdown_file.name, tenant_id)
        
        # Chunk the markdown content using structure-aware chunking
        print(f"   ⏳ Splitting into structure-aware chunks...")
        chunk_start = time.time()
        chunks = chunk_markdown(content, max_chunk_size=1000, overlap=100)
        chunk_time = time.time() - chunk_start
        print(f"   ✅ Created {len(chunks)} chunks in {chunk_time:.2f}s")
        
        # Show sample of chunks for debugging
        if chunks:
            avg_chunk_size = sum(len(c.split()) for c in chunks) / len(chunks)
            print(f"   📊 Average chunk size: {avg_chunk_size:.0f} words")
            print(f"   📊 First chunk preview: {chunks[0][:100]}...")
        
        # Embed and store chunks
        print(f"   ⏳ Storing chunks in vector database...")
        embed_start = time.time()
        embed_chunks(chunks, module, tenant_id, markdown_file.name)
        embed_time = time.time() - embed_start
        print(f"   ✅ Chunks stored in {embed_time:.2f}s")
        
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Markdown Documentation Loading Summary:")
        print(f"  • File: {markdown_file.name}")
        print(f"  • Characters: {len(content):,}")
        print(f"  • Chunks created: {len(chunks)}")
        print(f"  • Module: {module}")
        print(f"  • Total time: {total_time:.2f}s")
        print(f"{'='*60}\n")
        
        return len(chunks)
        
    except Exception as e:
        print(f"   ❌ Error processing markdown file: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def reload_markdown_docs(markdown_file: str = None, tenant_id: str = "default"):
    """
    Reload the markdown documentation file.
    Useful for refreshing the codebase knowledge when documentation is updated.
    """
    print("\n🔄 Reloading markdown documentation...")
    return load_markdown_docs(markdown_file=markdown_file, tenant_id=tenant_id)

