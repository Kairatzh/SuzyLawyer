# SuzyLawyer — Умный юридический помощник

Привет! SuzyLawyer — это твой AI-ассистент, который отвечает на юридические вопросы, опираясь на законы. Работает через Telegram и API, использует RAG, FAISS и Together LLM. Всё просто и по делу!

##  Что умеет?

-  Читает PDF с законами и нормативами
-  Умно сортирует результаты через cross-encoder
-  Даёт чёткие ответы с помощью Together LLM
-  Работает через FastAPI-эндпоинт
-  Общается в Telegram через бота

##  Технологии

| Компонент       | Инструмент                              |
|-----------------|-----------------------------------------|
| LLM             | meta-llama/Llama-3.3-70B-Instruct-Turbo |
| Embedding       | paraphrase-multilingual-MiniLM-L12-v2   |
| Reranker        | cross-encoder/ms-marco-MiniLM-L-6-v2    |
| Vector DB       | FAISS                                   |
| Backend API     | FastAPI                                 |
| Telegram Bot    | aiogram 3.x                             |

## ⚙️ Установка

1. Клонируй репо:
   ```bash
   git clone https://github.com/Kairatzh/SuzyLawyer.git
   cd SuzyLawyer
