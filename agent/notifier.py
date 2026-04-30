import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

async def send_alert(message: str, buttons: bool = True):
    """Send notification with approval buttons"""
    if not bot:
        print(f"[NOTIFICATION] {message}")
        return None

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Approve", callback_data="approve")]
    ]) if buttons else None

    msg = await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        reply_markup=keyboard
    )
    return msg.message_id

@dp.callback_query()
async def handle_approval(callback: types.CallbackQuery):
    if callback.data == "approve":
        await callback.answer("✅ Approved - Executing fix")
        return True
    return False

async def run_bot():
    if bot:
        await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())