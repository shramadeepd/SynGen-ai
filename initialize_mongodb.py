#!/usr/bin/env python3
"""
Initialize MongoDB with policy documents from Document_Repository
"""

import os
import json
from pymongo import MongoClient
import PyPDF2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def initialize_mongodb():
    """Initialize MongoDB with policy documents"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['syngen_documents']
    collection = db['policy_documents']
    
    # Clear existing documents
    collection.delete_many({})
    logger.info("Cleared existing documents from MongoDB")
    
    # Path to Document_Repository
    doc_repo_path = Path("/mnt/d/Coding/SynGen-ai/Document_Repository(dataco-global-policy-dataset)")
    
    if not doc_repo_path.exists():
        logger.error(f"Document repository not found at {doc_repo_path}")
        return
    
    documents = []
    doc_id = 1
    
    # Process all PDF files in the repository
    for pdf_file in doc_repo_path.glob("*.pdf"):
        logger.info(f"Processing {pdf_file.name}")
        
        # Extract text from PDF
        content = extract_text_from_pdf(pdf_file)
        
        if content:
            # Create document title from filename
            title = pdf_file.stem.replace('_', ' ').replace('-', ' ')
            
            # Create document object
            document = {
                "id": doc_id,
                "title": title,
                "content": content,
                "filename": pdf_file.name,
                "document_type": "policy",
                "source": "dataco-global-policy-dataset",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            documents.append(document)
            doc_id += 1
        else:
            logger.warning(f"No content extracted from {pdf_file.name}")
    
    # Insert documents into MongoDB
    if documents:
        result = collection.insert_many(documents)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into MongoDB")
        
        # Create indexes for better search performance
        collection.create_index([("title", "text"), ("content", "text")])
        collection.create_index("document_type")
        collection.create_index("source")
        logger.info("Created search indexes")
        
        # Print summary
        logger.info(f"MongoDB initialization complete:")
        logger.info(f"- Database: syngen_documents")
        logger.info(f"- Collection: policy_documents")
        logger.info(f"- Documents: {len(documents)}")
        
        # Show sample document titles
        logger.info("Sample documents:")
        for doc in documents[:5]:
            logger.info(f"  - {doc['title']}")
            
    else:
        logger.error("No documents found to insert")
    
    client.close()

if __name__ == "__main__":
    initialize_mongodb()