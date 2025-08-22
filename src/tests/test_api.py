import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Тесты для эндпоинта проверки здоровья"""
    
    def test_health_check(self):
        """Тест эндпоинта /health"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestQuestionEndpoint:
    """Тесты для эндпоинта /get_question"""
    
    def test_get_question_success(self):
        """Тест успешного запроса вопроса"""
        with patch('src.app.main.get_rag_answer') as mock_get_answer:
            mock_get_answer.return_value = "Это тестовый ответ на юридический вопрос."
            
            response = client.post(
                "/get_question",
                json={"question": "Какие документы нужны для регистрации ООО?"}
            )
            
            assert response.status_code == 200
            assert response.json() == {
                "answer": "Это тестовый ответ на юридический вопрос."
            }
            mock_get_answer.assert_called_once_with(
                "Какие документы нужны для регистрации ООО?",
                Mock()  #config
            )
    
    def test_get_question_missing_question(self):
        """Тест запроса без вопроса"""
        response = client.post(
            "/get_question",
            json={}
        )
        
        assert response.status_code == 422 
    
    def test_get_question_empty_question(self):
        """Тест запроса с пустым вопросом"""
        response = client.post(
            "/get_question",
            json={"question": ""}
        )
        
        assert response.status_code == 200  
    
    def test_get_question_invalid_json(self):
        """Тест запроса с неверным JSON"""
        response = client.post(
            "/get_question",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_get_question_rag_error(self):
        """Тест обработки ошибки RAG системы"""
        with patch('src.app.main.get_rag_answer') as mock_get_answer:
            mock_get_answer.side_effect = Exception("RAG error")
            
            response = client.post(
                "/get_question",
                json={"question": "Тестовый вопрос"}
            )
            
            assert response.status_code == 500


class TestAPIValidation:
    """Тесты валидации API"""
    
    def test_question_request_model(self):
        """Тест модели QuestionRequest"""
        from src.app.main import QuestionRequest
        
        valid_request = QuestionRequest(question="Валидный вопрос")
        assert valid_request.question == "Валидный вопрос"
        
        empty_request = QuestionRequest(question="")
        assert empty_request.question == ""
    
    def test_answer_response_model(self):
        """Тест модели AnswerResponse"""
        from src.app.main import AnswerResponse
        
        response = AnswerResponse(answer="Тестовый ответ")
        assert response.answer == "Тестовый ответ"


class TestAPIDocumentation:
    """Тесты документации API"""
    
    def test_openapi_schema(self):
        """Тест доступности OpenAPI схемы"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        assert "/health" in schema["paths"]
        assert "/get_question" in schema["paths"]
    
    def test_swagger_ui(self):
        """Тест доступности Swagger UI"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc(self):
        """Тест доступности ReDoc"""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestAPIErrorHandling:
    """Тесты обработки ошибок API"""
    
    def test_404_error(self):
        """Тест обработки 404 ошибки"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Тест обработки неподдерживаемого метода"""
        response = client.get("/get_question")
        
        assert response.status_code == 405  


if __name__ == "__main__":
    pytest.main([__file__])
