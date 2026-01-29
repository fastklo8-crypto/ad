import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
import logging
from datetime import datetime, timedelta

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфігурація
BOT_TOKEN = '8568797627:AAE8L71IRGsvER9LqcZ9eXTxNo3ZjKz92zU'  # Замінити на токен бота
CHAT_ID = '@troesh'  # Замінити на ID групи або каналу (напр. @назва_групи)

# Текст основного повідомлення
ADVERTISEMENT_TEXT = """📢 *Реклама в Троєщині — Прайс-лист*
🔝 *Закріплення від імені чату (оголошення зверху):*
• День: 500 грн. (економія 500 грн)
• Два дні: 1000 грн. (економія 1000 грн)
• Три дні: 1500 грн. (економія 1500 грн)
• П'ять діб: 2250 грн. (економія 2250 грн)
*Рекламний пост без закріплення (звичайне повідомлення в стрічці):*
• 1 пост: 250 грн.
• 10 постів: 2250 грн. (економія 250 грн.)
• 100 постів: 5000 грн. (економія 20000 грн.)
• 1000 постів: 10000 грн. (економія 240000 грн.)
*Реклама на аватарці чату:*
• 1 місяць: 5000 грн.
👉 *Для замовлення пишіть адмінам* ❤️"""

# Текст короткого повідомлення
SHORT_TEXT = "Запрошення для сусідів: t.me/troesh"

# Створюємо кнопку "Поділитися"
share_button = InlineKeyboardButton("Поділитися", url="https://t.me/share/url?url=t.me/troesh&text=Запрошення для сусідів")
keyboard = InlineKeyboardMarkup([[share_button]])

async def post_main_message():
    """Функція для відправки основного рекламного повідомлення"""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=ADVERTISEMENT_TEXT,
            parse_mode='Markdown'
        )
        logger.info(f"Основне повідомлення успішно відправлено до {CHAT_ID}")
        return True
    except TelegramError as e:
        logger.error(f"Помилка відправки основного повідомлення: {e}")
        return False

async def post_short_message():
    """Функція для відправки короткого повідомлення з посиланням"""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=SHORT_TEXT,
            reply_markup=keyboard,
            parse_mode=None
        )
        logger.info(f"Коротке повідомлення успішно відправлено до {CHAT_ID}")
        return True
    except TelegramError as e:
        logger.error(f"Помилка відправки короткого повідомлення: {e}")
        return False

async def schedule_messages():
    """Головна функція для планування повідомлень"""
    # Ініціалізуємо час першого запуску
    start_time = datetime.now()
    
    # Розраховуємо час наступного основного повідомлення (найближчий 4-годинний інтервал)
    hours_to_next_main = 4 - (start_time.hour % 4)
    next_main_time = start_time + timedelta(hours=hours_to_next_main)
    next_main_time = next_main_time.replace(minute=0, second=0, microsecond=0)
    
    # Перше коротке повідомлення - через 30 хвилин після основного
    next_short_time = next_main_time + timedelta(minutes=30)
    
    logger.info(f"Перше основне повідомлення о {next_main_time.strftime('%H:%M')}")
    logger.info(f"Перше коротке повідомлення о {next_short_time.strftime('%H:%M')}")
    
    while True:
        current_time = datetime.now()
        
        # Перевіряємо чи час для основного повідомлення
        if current_time >= next_main_time:
            await post_main_message()
            # Оновлюємо час наступного основного повідомлення
            next_main_time += timedelta(hours=4)
            # Оновлюємо час наступного короткого повідомлення
            next_short_time = next_main_time + timedelta(minutes=30)
            logger.info(f"Наступне основне повідомлення о {next_main_time.strftime('%H:%M')}")
            logger.info(f"Наступне коротке повідомлення о {next_short_time.strftime('%H:%M')}")
        
        # Перевіряємо чи час для короткого повідомлення
        if current_time >= next_short_time:
            await post_short_message()
            # Оновлюємо час наступного короткого повідомлення
            next_short_time += timedelta(hours=1)
            logger.info(f"Наступне коротке повідомлення о {next_short_time.strftime('%H:%M')}")
        
        # Чекаємо 30 секунд перед наступною перевіркою
        await asyncio.sleep(30)

async def main():
    """Запуск бота"""
    logger.info("Бот запущено. Початок планування повідомлень...")
    await schedule_messages()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено користувачем.")