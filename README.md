# SuzyLawyer — Умный юридический помощник

## Описание
SuzyLawyer — это AI-ассистент для ответов на юридические вопросы, основанный на казахском законодательстве. Система использует технологию RAG (Retrieval-Augmented Generation) для поиска релевантных правовых документов и генерации точных ответов.

**Кратко:**
-  Отвечает на юридические вопросы на основе российского законодательства
-  Анализирует PDF-документы с правовыми актами
-  Использует умный поиск с cross-encoder для точности
-  Работает через Telegram-бота и REST API
-  Генерирует ответы с помощью Together LLM

**Для кого:**
- Юристы и правоведы
- Студенты юридических факультетов
- Граждане, ищущие правовую информацию
- Разработчики, интегрирующие правовые AI-решения

**Основные задачи:**
- Быстрый поиск релевантных правовых норм
- Генерация понятных ответов на юридические вопросы
- Обеспечение доступа к правовой информации через удобные интерфейсы

## Демонстрация
[Здесь будет размещена демонстрация на хостинге]

## Требования к системе
- **Python**: версия 3.9 или выше
- **Docker**: версия 20.10 или выше
- **Docker Compose**: версия 2.0 или выше

### Проверка версий
```bash
# Проверка Python
python --version

# Проверка Docker
docker --version

# Проверка Docker Compose
docker compose version
```

## Быстрый старт
Минимальный набор команд для запуска приложения "из коробки":

```bash
# Клонирование репозитория
git clone https://github.com/Kairatzh/SuzyLawyer.git
cd SuzyLawyer

# Запуск приложения в Docker
make up

# Остановка приложения
make down
```

## Установка зависимостей
```bash
# Установка Python-зависимостей
pip install -r requirements.txt
```

## Настройка переменных окружения
Скопируйте файл `.env.example` в `.env` и заполните необходимые переменные:

```bash
cp .env.example .env
```

См. пример в [.env.example](.env.example)

**Обязательные переменные:**
- `BOT_TOKEN` — токен Telegram-бота (получить у @BotFather)
- `TOGETHER_API_KEY` — API-ключ Together AI для доступа к LLM
- `FASTAPI_HOST` — хост для FastAPI (по умолчанию: http://localhost:8000)
- `PDF_PATH` — путь к PDF-файлу с законодательством
- `VECTOR_STORE_PATH` — путь для сохранения векторной базы данных

## Запуск приложения

### Запуск через Docker Compose (рекомендуется)
```bash
# Запуск всех сервисов
make up

# Запуск в фоновом режиме
make up-detached

# Остановка
make down

# Просмотр логов
make logs
```

### Запуск в режиме разработки
```bash
# Запуск FastAPI сервера
cd src
uvicorn app.main:app --host localhost --port 8000 --reload --log-level debug

# Запуск Telegram-бота (в отдельном терминале)
cd src
python app/bot.py
```

### Запуск в промышленной среде
```bash
# Запуск с продакшн-конфигурацией
docker compose -f docker-compose.prod.yml up -d
```

## Использование

### REST API
```bash
# Запрос к API
curl -X 'POST' \
  'http://localhost:8000/get_question' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Какие документы нужны для регистрации ООО?"
  }'

# Формат ответа
{
  "answer": "Для регистрации ООО необходимы следующие документы..."
}

# Проверка здоровья сервиса
curl http://localhost:8000/health
```

### Telegram-бот
1. Найдите бота в Telegram по токену
2. Отправьте команду `/start`
3. Задайте юридический вопрос
4. Получите ответ на основе законодательства

## Структура проекта
```
SuzyLawyer/
├── src/
│   ├── app/                    # Основное приложение
│   │   ├── main.py            # FastAPI сервер
│   │   └── bot.py             # Telegram-бот
│   ├── rag_main/              # RAG система
│   │   ├── rag_system.py      # Конфигурация и индексация
│   │   ├── rag_inference.py   # Логика ответов
│   │   └── rag_reranker.py    # Переранжирование результатов
│   ├── prompt/                # Шаблоны промптов
│   │   └── templates/
│   ├── datasets/              # Правовые документы
│   │   └── kodeks.pdf         # PDF с законодательством
│   ├── vectordb/              # Векторная база данных
│   ├── utils/                 # Вспомогательные модули
│   │   └── logger.py          # Логирование
│   └── tests/                 # Тесты
├── docker-compose.yml         # Docker Compose конфигурация
├── docker-compose.prod.yml    # Продакшн конфигурация
├── Dockerfile                 # Docker образ
├── Makefile                   # Команды для управления
├── requirements.txt           # Python зависимости
├── .env.example              # Пример переменных окружения
└── README.md                 # Документация
```

## Тесты
Запуск тестов производится с помощью [pytest](https://pypi.org/project/pytest/):

```bash
# Запуск всех тестов
pytest src/tests/

# Запуск с подробным выводом
pytest src/tests/ -v

# Запуск конкретного теста
pytest src/tests/test_rag_system.py

# Запуск с покрытием кода
pytest src/tests/ --cov=src --cov-report=html
```

## Качество кода
```bash
# Линтер
flake8 src/ --max-line-length=120

# Форматтер
black src/ --check

# Статический анализ типов
mypy src/

# Безопасность
bandit src/
```

## API Документация
После запуска приложения доступна автоматическая документация:
- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [OpenAPI спецификация](http://localhost:8000/openapi.json)

## Технологии
| Компонент       | Инструмент                              |
|-----------------|-----------------------------------------|
| LLM             | meta-llama/Llama-3.3-70B-Instruct-Turbo |
| Embedding       | paraphrase-multilingual-MiniLM-L12-v2   |
| Reranker        | cross-encoder/ms-marco-MiniLM-L-6-v2    |
| Vector DB       | FAISS                                   |
| Backend API     | FastAPI                                 |
| Telegram Bot    | aiogram 3.x                             |
| Контейнеризация | Docker & Docker Compose                 |
| Управление      | Make                                    |

## Лицензия
MIT License

## Поддержка
- Создайте Issue в GitHub для сообщения о багах
- Предложения по улучшению приветствуются через Pull Request
