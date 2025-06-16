
import logging
import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import Together
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from src.rag_main.rag_reranker import RAGReranker

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    vector_store_path: str = "C:/Users/User/Desktop/SuzyLawyer/src/vectordb"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: int = 3
    llm_model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    max_tokens: int = 512

def get_rag_answer(query: str, config: RAGConfig) -> str:
    logger.info("Загрузка индекса")
    embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
    db = FAISS.load_local(config.vector_store_path, embeddings, allow_dangerous_deserialization=True)

    retriever = db.as_retriever(search_kwargs={"k": config.top_k * 3})
    raw_docs = retriever.invoke(query)

    reranker = RAGReranker(config.rerank_model)
    reranked_docs = reranker.rerank(query, raw_docs, top_k=config.top_k)

    class FixedCompressor(BaseDocumentCompressor):
        def compress_documents(self, documents: List[Document], query: str, *, callbacks=None, **kwargs) -> List[Document]:
            return reranked_docs

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=FixedCompressor(),
        base_retriever=retriever
    )

    llm = Together(
        model=config.llm_model,
        temperature=0.7,
        max_tokens=config.max_tokens,
        together_api_key=os.getenv("TOGETHER_API_KEY")
    )

    prompt = PromptTemplate(
        template=(
            "Ты юридический помощник, отвечающий строго на основе положений закона. "
            "Используй приведённый ниже фрагмент закона (контекст), чтобы дать краткий, точный и официальный ответ на вопрос. "
            "Если ответа нет в тексте, прямо скажи об этом и не выдумывай.\n\n"
            "\ud83d\udcd8 Контекст:\n{context}\n\n"
            "\u2753 Вопрос:\n{question}\n\n"
            "\u2696\ufe0f Ответ:"
        ),
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=compression_retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    result = qa_chain.invoke({"query": query})
    return result["result"]
