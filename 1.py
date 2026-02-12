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

# Налаштування часу роботи
WORK_START_HOUR = 9  # Початок роботи о 9:00
WORK_END_HOUR = 23   # Кінець роботи о 23:00
MIN_INTERVAL_MINUTES = 30  # Мінімальний інтервал між повідомленнями

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
share_button = InlineKeyboardButton("Поділитися", url="https://t.me/share/url?url=https://t.me/troesh&text=Запрошую до чату Троєщини!")
share_keyboard = InlineKeyboardMarkup([[share_button]])

# Нове повідомлення про адміністратора
ADMIN_TEXT = """*Хочеш стати адміністратором троєщини безкоштоно?*

Отримай можливість допомагати людям та розвивати чат разом з нами!"""
admin_button = InlineKeyboardButton("Деталі", url="https://telegra.ph/STAN-ADM%D0%86NOM-BEZKOSHTOVNO-02-12")
admin_keyboard = InlineKeyboardMarkup([[admin_button]])

async def is_working_time():
    """Перевірка чи зараз робочий час"""
    current_hour = datetime.now().hour
    return WORK_START_HOUR <= current_hour < WORK_END_HOUR

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
            reply_markup=share_keyboard,
            parse_mode=None,
            disable_web_page_preview=False
        )
        logger.info(f"Коротке повідомлення успішно відправлено до {CHAT_ID}")
        return True
    except TelegramError as e:
        logger.error(f"Помилка відправки короткого повідомлення: {e}")
        return False

async def post_admin_message():
    """Функція для відправки повідомлення про адміністратора"""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=ADMIN_TEXT,
            parse_mode='Markdown',
            reply_markup=admin_keyboard
        )
        logger.info(f"Повідомлення про адміністратора успішно відправлено до {CHAT_ID}")
        return True
    except TelegramError as e:
        logger.error(f"Помилка відправки повідомлення про адміністратора: {e}")
        return False

async def schedule_messages():
    """Головна функція для планування повідомлень"""
    last_message_time = None
    
    # Спочатку відправляємо тестове повідомлення для перевірки
    logger.info("Відправка тестового повідомлення з кнопкою...")
    test_sent = await post_short_message()
    if test_sent:
        last_message_time = datetime.now()
        logger.info("Тестове повідомлення успішно відправлено!")
    else:
        logger.error("Не вдалося відправити тестове повідомлення!")
    
    # Ініціалізуємо час першого запуску
    start_time = datetime.now()
    
    # Розраховуємо час наступного основного повідомлення
    next_main_time = start_time.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
    if next_main_time <= start_time:
        next_main_time += timedelta(days=1)
    
    # Розраховуємо час наступного короткого повідомлення
    next_short_time = start_time.replace(minute=0, second=0, microsecond=0)
    while next_short_time <= start_time or next_short_time.hour >= WORK_END_HOUR or next_short_time.hour < WORK_START_HOUR:
        next_short_time += timedelta(hours=1)
        if next_short_time.hour >= WORK_END_HOUR:
            next_short_time = next_short_time.replace(hour=WORK_START_HOUR, minute=0) + timedelta(days=1)
    
    # Розраховуємо час першого повідомлення про адміністратора
    next_admin_time = start_time.replace(hour=WORK_START_HOUR + 2, minute=0, second=0, microsecond=0)
    if next_admin_time <= start_time:
        next_admin_time += timedelta(days=1)
    
    logger.info(f"Робочий час: з {WORK_START_HOUR}:00 до {WORK_END_HOUR}:00")
    logger.info(f"Мінімальний інтервал між повідомленнями: {MIN_INTERVAL_MINUTES} хвилин")
    logger.info(f"Перше основне повідомлення о {next_main_time.strftime('%H:%M %d.%m.%Y')}")
    logger.info(f"Перше коротке повідомлення о {next_short_time.strftime('%H:%M %d.%m.%Y')}")
    logger.info(f"Перше повідомлення про адміна о {next_admin_time.strftime('%H:%M %d.%m.%Y')}")
    
    while True:
        current_time = datetime.now()
        
        # Перевіряємо чи зараз робочий час
        if not await is_working_time():
            # Якщо не робочий час - чекаємо до початку
            next_work_time = current_time.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
            if next_work_time <= current_time:
                next_work_time += timedelta(days=1)
            sleep_seconds = (next_work_time - current_time).total_seconds()
            logger.info(f"Нічний режим. Наступне повідомлення о {next_work_time.strftime('%H:%M %d.%m.%Y')}")
            await asyncio.sleep(sleep_seconds)
            continue
        
        can_send = True
        if last_message_time:
            time_since_last = (current_time - last_message_time).total_seconds() / 60
            if time_since_last < MIN_INTERVAL_MINUTES:
                can_send = False
                wait_time = MIN_INTERVAL_MINUTES - time_since_last
                logger.info(f"Очікування {wait_time:.0f} хвилин перед наступним повідомленням")
                await asyncio.sleep(wait_time * 60)
                continue
        
        # Перевіряємо чи час для повідомлень
        message_sent = False
        
        if can_send and current_time >= next_main_time:
            await post_main_message()
            next_main_time += timedelta(hours=4)
            last_message_time = datetime.now()
            message_sent = True
            logger.info(f"Наступне основне повідомлення о {next_main_time.strftime('%H:%M %d.%m.%Y')}")
        
        if can_send and not message_sent and current_time >= next_short_time:
            await post_short_message()
            next_short_time += timedelta(hours=1)
            last_message_time = datetime.now()
            message_sent = True
            logger.info(f"Наступне коротке повідомлення о {next_short_time.strftime('%H:%M %d.%m.%Y')}")
        
        if can_send and not message_sent and current_time >= next_admin_time:
            await post_admin_message()
            # Відправляємо повідомлення про адміна кожні 3 години
            next_admin_time += timedelta(hours=3)
            last_message_time = datetime.now()
            message_sent = True
            logger.info(f"Наступне повідомлення про адміна о {next_admin_time.strftime('%H:%M %d.%m.%Y')}")
        
        # Якщо жодне повідомлення не відправлено, чекаємо 30 секунд
        if not message_sent:
            await asyncio.sleep(30)
        else:
            # Чекаємо мінімальний інтервал перед наступною відправкою
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