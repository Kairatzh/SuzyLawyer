import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from aiogram.types import Message, User, Chat
from src.app.bot import start, handle_question


class TestBotHandlers:
    """Тесты для обработчиков Telegram бота"""
    
    @pytest.fixture
    def mock_message(self):
        """Фикстура для создания мок-сообщения"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456
        message.chat = Mock(spec=Chat)
        message.chat.id = 123456
        message.answer = AsyncMock()
        message.reply = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_message):
        """Тест команды /start"""
        await start(mock_message)
        
        mock_message.answer.assert_called_once_with(
            "👋 Привет! Отправь юридический вопрос, и я постараюсь ответить согласно закону."
        )
    
    @pytest.mark.asyncio
    async def test_handle_question_success(self, mock_message):
        """Тест успешной обработки вопроса"""
        mock_message.text = "Какие документы нужны для регистрации ООО?"
        
        with patch('src.app.bot.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "answer": "Для регистрации ООО необходимы следующие документы..."
            })
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            mock_context.__aexit__.return_value = None
            
            mock_session.return_value.post.return_value = mock_context
            
            await handle_question(mock_message)
            
            mock_message.reply.assert_called_once_with(
                "⚖️ <b>Ответ:</b>\nДля регистрации ООО необходимы следующие документы..."
            )
    
    @pytest.mark.asyncio
    async def test_handle_question_api_error(self, mock_message):
        """Тест обработки ошибки API"""
        mock_message.text = "Тестовый вопрос"
        
        with patch('src.app.bot.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            mock_context.__aexit__.return_value = None
            
            mock_session.return_value.post.return_value = mock_context
            
            await handle_question(mock_message)
            
            mock_message.reply.assert_called_once_with(
                "⚠️ Не удалось получить ответ. Попробуй позже."
            )
    
    @pytest.mark.asyncio
    async def test_handle_question_connection_error(self, mock_message):
        """Тест обработки ошибки соединения"""
        mock_message.text = "Тестовый вопрос"
        
        with patch('src.app.bot.aiohttp.ClientSession') as mock_session:
            mock_session.side_effect = Exception("Connection error")
            
            await handle_question(mock_message)
            
            mock_message.reply.assert_called_once_with(
                "❌ Внутренняя ошибка сервера. Попробуй позже."
            )
    
    @pytest.mark.asyncio
    async def test_handle_question_empty_text(self, mock_message):
        """Тест обработки пустого текста"""
        mock_message.text = "   "  # Только пробелы
        
        await handle_question(mock_message)
        
        # Должен быть вызван API с пустой строкой
        mock_message.reply.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_question_strips_whitespace(self, mock_message):
        """Тест удаления лишних пробелов"""
        mock_message.text = "  Вопрос с пробелами  "
        
        with patch('src.app.bot.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"answer": "Ответ"})
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            mock_context.__aexit__.return_value = None
            
            mock_session.return_value.post.return_value = mock_context
            
            await handle_question(mock_message)
            
            # Проверяем, что в API отправляется текст без лишних пробелов
            mock_session.return_value.post.assert_called_once()
            call_args = mock_session.return_value.post.call_args
            assert "Вопрос с пробелами" in str(call_args)


class TestBotConfiguration:
    """Тесты конфигурации бота"""
    
    @patch.dict(os.environ, {
        'BOT_TOKEN': 'test_token_123',
        'FASTAPI_HOST': 'http://test-host:8000'
    })
    def test_bot_configuration_from_env(self):
        """Тест загрузки конфигурации из переменных окружения"""
        # Перезагружаем модуль для применения новых переменных окружения
        import importlib
        import src.app.bot
        importlib.reload(src.app.bot)
        
        assert src.app.bot.BOT_TOKEN == 'test_token_123'
        assert src.app.bot.FASTAPI_HOST == 'http://test-host:8000'
    
    def test_bot_configuration_defaults(self):
        """Тест значений по умолчанию"""
        # Восстанавливаем оригинальные значения
        import importlib
        import src.app.bot
        importlib.reload(src.app.bot)
        
        assert src.app.bot.FASTAPI_HOST == "http://localhost:8000"


class TestBotInitialization:
    """Тесты инициализации бота"""
    
    @patch('src.app.bot.Bot')
    @patch('src.app.bot.Dispatcher')
    def test_bot_initialization(self, mock_dispatcher, mock_bot):
        """Тест инициализации бота и диспетчера"""
        import src.app.bot
        
        # Проверяем, что Bot и Dispatcher были созданы
        mock_bot.assert_called_once()
        mock_dispatcher.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
