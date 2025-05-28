#!/usr/bin/env python3
"""
SynGen AI Document Loader
Loads PDF documents from Document_Repository into a simple file-based storage
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.warning(f"Could not extract text from {pdf_path}: {e}")
        return ""

def load_documents():
    """Load all PDF documents and create metadata"""
    
    # Document directory
    doc_dir = Path("/mnt/d/Coding/SynGen-ai/Document_Repository(dataco-global-policy-dataset)")
    
    # Output directory for processed documents
    output_dir = Path("/mnt/d/Coding/SynGen-ai/Backend/data/documents")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    documents = []
    
    # Process each PDF file
    for pdf_file in doc_dir.glob("*.pdf"):
        logger.info(f"Processing {pdf_file.name}")
        
        # Extract text
        text_content = extract_pdf_text(str(pdf_file))
        
        # Create document metadata
        doc_info = {
            "id": len(documents) + 1,
            "filename": pdf_file.name,
            "title": pdf_file.stem.replace("_", " ").title(),
            "type": "policy_document",
            "category": "supply_chain_policy",
            "content": text_content,
            "file_size": pdf_file.stat().st_size,
            "file_path": str(pdf_file),
            "processed_date": "2024-01-01"
        }
        
        documents.append(doc_info)
        
        # Save individual document
        doc_output_file = output_dir / f"{pdf_file.stem}.json"
        with open(doc_output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_info, f, indent=2)
    
    # Save all documents metadata
    all_docs_file = output_dir / "all_documents.json"
    with open(all_docs_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2)
    
    logger.info(f"Processed {len(documents)} documents")
    logger.info(f"Documents saved to {output_dir}")
    
    return documents

def create_simple_search_index(documents: List[Dict[str, Any]]):
    """Create a simple search index for the documents"""
    
    output_dir = Path("/mnt/d/Coding/SynGen-ai/Backend/data/documents")
    
    # Create keyword index
    keyword_index = {}
    
    for doc in documents:
        doc_id = doc["id"]
        content = doc["content"].lower()
        title = doc["title"].lower()
        
        # Extract keywords (simple approach)
        words = set()
        
        # Add title words
        words.update(title.split())
        
        # Add content words (limit to avoid huge index)
        content_words = content.split()[:1000]  # First 1000 words
        words.update(content_words)
        
        # Filter out common words and short words
        filtered_words = {
            word.strip('.,!?;:"()[]{}') 
            for word in words 
            if len(word) > 3 and word.isalpha()
        }
        
        # Add to index
        for word in filtered_words:
            if word not in keyword_index:
                keyword_index[word] = []
            if doc_id not in keyword_index[word]:
                keyword_index[word].append(doc_id)
    
    # Save keyword index
    index_file = output_dir / "keyword_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(keyword_index, f, indent=2)
    
    logger.info(f"Created keyword index with {len(keyword_index)} keywords")

def main():
    """Main function"""
    try:
        logger.info("Starting document loading process...")
        
        # Load documents
        documents = load_documents()
        
        # Create search index
        create_simple_search_index(documents)
        
        logger.info("Document loading completed successfully!")
        
        # Print summary
        print(f"\nDocument Loading Summary:")
        print(f"========================")
        print(f"Total documents processed: {len(documents)}")
        
        categories = {}
        for doc in documents:
            cat = doc.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"Categories:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count}")
        
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        raise

if __name__ == "__main__":
    main()