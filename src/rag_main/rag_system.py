import logging
import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    pdf_path: str = "C:/Users/User/Desktop/SuzyLawyer/src/datasets/kodeks.pdf"
    vector_store_path: str = "/src/vectordb"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 150

def load_pdf(config: RAGConfig) -> List[Document]:
    logger.info("Загрузка PDF")
    loader = PyPDFLoader(config.pdf_path)
    docs = loader.load()
    return [
        doc for doc in docs
        if len(doc.page_content.strip()) > 30 and "..." not in doc.page_content
    ]

def split_docs(docs: List[Document], config: RAGConfig) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap
    )
    return splitter.split_documents(docs)

def build_faiss_index(docs: List[Document], config: RAGConfig):
    logger.info("Создание FAISS индекса")
    embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(config.vector_store_path)
    logger.info("Индекс сохранён")

if __name__ == "__main__":
    config = RAGConfig()
    docs = load_pdf(config)
    chunks = split_docs(docs, config)
    build_faiss_index(chunks, config)
