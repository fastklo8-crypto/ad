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
BOT_TOKEN = '8568797627:AAE8L71IRGsvER9LqcZ9eXTxNo3ZjKz92zU'
CHAT_ID = '@troesh'

# Текст основного повідомлення
ADVERTISEMENT_TEXT = """📢 Реклама на Троєщині — Прайс-лист
📌 Пост від імені чату (звичайне оголошення):
• 4 поста на день: 1000 грн.
📅 Пакетні пропозиції:
• Тиждень (35 постів): 4000 грн.
• Місяць (150 постів): 10000 грн. 
• 3 місяці (450 постів): 30000 грн.  
• 6 місяців (900 постів): 50000 грн. 
🔝 Закріплення від імені чату (оголошення зверху):
• Два дні: 1000 грн. 
• Три дні: 1500 грн.
• П'ять діб: 2500 грн. 
🖼 Реклама на аватарці чату:
• 1 місяць: 5000 грн. (акція: +1 тиждень пакету в подарунок!)
👉 Для замовлення пишіть адмінам ❤️"""

SHORT_TEXT = "Запроси друзів та сусідів до чату\n\n"
share_button = InlineKeyboardButton("Поділитися", url="https://t.me/share/url?url=https://t.me/+SOp8Ag6O2B81NmFi&text=Запрошую до чату Троєщини!")
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
            parse_mode=None,
            disable_web_page_preview=False  # Явно включаем предпросмотр ссылки
        )
        logger.info(f"Коротке повідомлення успішно відправлено до {CHAT_ID}")
        return True
    except TelegramError as e:
        logger.error(f"Помилка відправки короткого повідомлення: {e}")
        return False

async def schedule_messages():
    """Головна функція для планування повідомлень"""
    # Сначала отправляем тестовое сообщение для проверки
    logger.info("Отправка тестового сообщения с кнопкой...")
    test_sent = await post_short_message()
    if test_sent:
        logger.info("Тестовое сообщение успешно отправлено!")
    else:
        logger.error("Не удалось отправить тестовое сообщение!")
    
    # Ініціалізуємо час першого запуску
    start_time = datetime.now()
    
    # Розраховуємо час наступного основного повідомлення (найближчий 4-годинний інтервал)
    hours_to_next_main = 4 - (start_time.hour % 4)
    next_main_time = start_time + timedelta(hours=hours_to_next_main)
    next_main_time = next_main_time.replace(minute=0, second=0, microsecond=0)
    
    # Коротке повідомлення - кожну годину, починаючи з найближчої години
    next_short_time = start_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    logger.info(f"Перше основне повідомлення о {next_main_time.strftime('%H:%M')}")
    logger.info(f"Перше коротке повідомлення о {next_short_time.strftime('%H:%M')}")
    
    while True:
        current_time = datetime.now()
        
        # Перевіряємо чи час для основного повідомлення
        if current_time >= next_main_time:
            await post_main_message()
            # Оновлюємо час наступного основного повідомлення
            next_main_time += timedelta(hours=4)
            logger.info(f"Наступне основне повідомлення о {next_main_time.strftime('%H:%M')}")
        
        # Перевіряємо чи час для короткого повідомлення (кожну годину)
        if current_time >= next_short_time:
            await post_short_message()
            # Оновлюємо час наступного короткого повідомлення (через 1 годину)
            next_short_time += timedelta(hours=1)
            logger.info(f"Наступне коротке повідомлення о {next_short_time.strftime('%H:%M')}")
        
        # Чекаємо 60 секунд перед наступною перевіркою
        await asyncio.sleep(60)

async def main():
    """Запуск бота"""
    logger.info("Бот запущено. Початок планування повідомлень...")
    await schedule_messages()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено користувачем.")