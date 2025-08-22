import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.rag_main.rag_system import RAGConfig, load_pdf, split_docs, build_faiss_index


class TestRAGConfig:
    """Тесты для класса RAGConfig"""
    
    def test_rag_config_default_values(self):
        """Тест значений по умолчанию"""
        config = RAGConfig()
        
        assert config.pdf_path == "src/datasets/kodeks.pdf"
        assert config.vector_store_path == "src/vectordb"
        assert config.embedding_model == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 150
    
    @patch.dict(os.environ, {
        'PDF_PATH': '/custom/path/file.pdf',
        'VECTOR_STORE_PATH': '/custom/vectordb',
        'EMBEDDING_MODEL': 'custom/model',
        'CHUNK_SIZE': '500',
        'CHUNK_OVERLAP': '100'
    })
    def test_rag_config_from_env(self):
        """Тест загрузки значений из переменных окружения"""
        config = RAGConfig()
        
        assert config.pdf_path == "/custom/path/file.pdf"
        assert config.vector_store_path == "/custom/vectordb"
        assert config.embedding_model == "custom/model"
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100


class TestLoadPDF:
    """Тесты для функции load_pdf"""
    
    @patch('src.rag_main.rag_system.PyPDFLoader')
    def test_load_pdf_success(self, mock_loader):
        """Тест успешной загрузки PDF"""

        mock_doc1 = Mock()
        mock_doc1.page_content = "Это длинный текст документа с содержанием больше 30 символов"
        
        mock_doc2 = Mock()
        mock_doc2.page_content = "Короткий"
        
        mock_doc3 = Mock()
        mock_doc3.page_content = "Текст с многоточием..."
        
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc1, mock_doc2, mock_doc3]
        mock_loader.return_value = mock_loader_instance
        
        config = RAGConfig()
        result = load_pdf(config)
        
        assert len(result) == 1
        assert result[0].page_content == "Это длинный текст документа с содержанием больше 30 символов"
        mock_loader.assert_called_once_with(config.pdf_path)


class TestSplitDocs:
    """Тесты для функции split_docs"""
    
    def test_split_docs(self):
        """Тест разделения документов"""
        from langchain.schema import Document
        
        docs = [
            Document(page_content="Это очень длинный текст, который должен быть разделен на части. " * 50),
            Document(page_content="Второй документ с текстом для разделения. " * 30)
        ]
        
        config = RAGConfig(chunk_size=100, chunk_overlap=20)
        result = split_docs(docs, config)
        
        assert len(result) > len(docs)
        
        for chunk in result:
            assert len(chunk.page_content) <= config.chunk_size + 50  


class TestBuildFAISSIndex:
    """Тесты для функции build_faiss_index"""
    
    @patch('src.rag_main.rag_system.HuggingFaceEmbeddings')
    @patch('src.rag_main.rag_system.FAISS')
    def test_build_faiss_index(self, mock_faiss, mock_embeddings):
        """Тест создания FAISS индекса"""
        from langchain.schema import Document
        
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_faiss_instance = Mock()
        mock_faiss.from_documents.return_value = mock_faiss_instance
        
        docs = [
            Document(page_content="Тестовый документ 1"),
            Document(page_content="Тестовый документ 2")
        ]
        
        config = RAGConfig()
        
        build_faiss_index(docs, config)
        
        mock_embeddings.assert_called_once_with(model_name=config.embedding_model)
        
        mock_faiss.from_documents.assert_called_once_with(docs, mock_embeddings_instance)
        
        mock_faiss_instance.save_local.assert_called_once_with(config.vector_store_path)


class TestIntegration:
    """Интеграционные тесты"""
    
    @patch('src.rag_main.rag_system.load_pdf')
    @patch('src.rag_main.rag_system.split_docs')
    @patch('src.rag_main.rag_system.build_faiss_index')
    def test_main_workflow(self, mock_build, mock_split, mock_load):
        """Тест основного workflow"""
        from langchain.schema import Document
        
        mock_docs = [Document(page_content="Тестовый документ")]
        mock_chunks = [Document(page_content="Тестовый чанк")]
        
        mock_load.return_value = mock_docs
        mock_split.return_value = mock_chunks
        
        config = RAGConfig()
        
        docs = load_pdf(config)
        chunks = split_docs(docs, config)
        build_faiss_index(chunks, config)
        
        mock_load.assert_called_once_with(config)
        mock_split.assert_called_once_with(mock_docs, config)
        mock_build.assert_called_once_with(mock_chunks, config)


if __name__ == "__main__":
    pytest.main([__file__])
