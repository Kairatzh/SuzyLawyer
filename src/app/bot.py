import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Отправь юридический вопрос, и я постараюсь ответить согласно закону.")

@dp.message(F.text)
async def handle_question(message: Message):
    user_question = message.text.strip()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{FASTAPI_HOST}/get_question", json={"question": user_question}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await message.reply(f"⚖️ <b>Ответ:</b>\n{data['answer']}")
                else:
                    await message.reply("⚠️ Не удалось получить ответ. Попробуй позже.")
        except Exception as e:
            logging.error(f"Ошибка при запросе к API: {e}")
            await message.reply("❌ Внутренняя ошибка сервера. Попробуй позже.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
