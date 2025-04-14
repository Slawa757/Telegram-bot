import logging
import asyncio
import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("sk-bfcd6b0adfad4e46ac96e49e30ea321d")
TELEGRAM_BOT_TOKEN = os.getenv("7819860080:AAFRf49OWrp4iO8b3O_8ppsMcUs3Z1ui5M0")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def call_deepseek_api(user_input: str) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    try:
        reply = await call_deepseek_api(user_input)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен...")
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True,
            allowed_updates=["message"]
        )
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("🤖 Бот остановлен пользователем...")
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
    finally:
        print("🤖 Бот завершает работу...")
        try:
            if app.updater is not None and app.updater.running:
                await app.updater.stop()
            if app.running:
                await app.stop()
            await app.shutdown()
        except Exception as e:
            print(f"Ошибка при остановке: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        print("Event loop is already running. Запусти скрипт в отдельном процессе.")
    else:
        try:
            loop.run_until_complete(main())
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
