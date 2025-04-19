import logging
from keep_alive import keep_alive
from telegram import InputFile
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния анкеты
(CHOOSING_ACTION, ENTER_NAME, CHOOSE_GENRE, ENTER_OTHER_GENRE, 
 ENTER_DURATION, ENTER_REQUIREMENTS, ENTER_CONTACT) = range(7)

# chat_id группы/канала, куда будут приходить заявки
GROUP_CHAT_ID = -1002542936379  # Замени на свой chat_id

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Подать заявку")],
        [KeyboardButton("Узнать подробнее")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    with open("welcome.jpg", "rb") as photo:
        await update.message.reply_photo(
            photo=InputFile(photo),
            caption="👋 Привет! Ты хочешь выступить на «Петербургском квартирнике»? 🎭✨\n"
                    "Заполни короткую заявку, и мы свяжемся с тобой!",
            reply_markup=reply_markup
        )

    return CHOOSING_ACTION

# Подробности
async def more_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Подать заявку")],
        [KeyboardButton("Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "📌 Квартирник – это творческий вечер, где выступают музыканты, поэты, актёры и другие артисты. "
        "Всё проходит в уютном лофте, а главная награда – искренние аплодисменты.\n"
        "🚀 Если ты готов(а) выступить – нажимай «Подать заявку»!",
        reply_markup=reply_markup
    )
    return CHOOSING_ACTION

# Начало заявки
async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("✅ Отлично! Теперь заполним анкету.\n\n1. Как тебя зовут?")
    return ENTER_NAME

# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text

    keyboard = [
        [KeyboardButton("Вокал 🎤"), KeyboardButton("Авторская музыка 🎸")],
        [KeyboardButton("Поэзия 📖"), KeyboardButton("Театр 🎭")],
        [KeyboardButton("Другое 📝")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("2. В каком жанре ты хочешь выступить?", reply_markup=reply_markup)
    return CHOOSE_GENRE

# Жанр
async def get_genre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    genre = update.message.text
    context.user_data['genre'] = genre

    if genre == "Другое 📝":
        await update.message.reply_text("👉 Напиши, что именно ты хочешь представить!")
        return ENTER_OTHER_GENRE

    await update.message.reply_text("3. Сколько примерно займёт твоё выступление?")
    return ENTER_DURATION

# Длительность
async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("4. Нужны ли тебе особые условия? (Микрофон, колонка и т.д.)")
    return ENTER_REQUIREMENTS

# Особые условия
async def get_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['requirements'] = update.message.text
    await update.message.reply_text("5. Контактный телефон или Telegram для связи")
    return ENTER_CONTACT

# Завершение заявки
async def complete_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact'] = update.message.text

    msg = (
        "🎭 Новая заявка на Петербургский квартирник:\n\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"🎨 Жанр: {context.user_data['genre']}\n"
        f"⏱ Длительность: {context.user_data['duration']}\n"
        f"🎚 Особые условия: {context.user_data['requirements']}\n"
        f"📞 Контакт: {context.user_data['contact']}"
    )

    # Отправка заявки в группу
    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в группу: {e}")

    # Ответ пользователю
    keyboard = [
        [KeyboardButton("Следить за новостями")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "📌 Спасибо! Твоя заявка принята!\n"
        "🎭 Организаторы скоро свяжутся с тобой. А пока – следи за новостями и готовь своё выступление!",
        reply_markup=reply_markup
    )

    # Отправка сообщения с inline-кнопкой для пересылки
    share_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="📣 Поделиться с друзьями",
            switch_inline_query="Присоединяйся к Петербургскому квартирнику! 🎭✨ https://t.me/peterburgkvartirnik"
        )
    ]])

    await update.message.reply_text(
        "🎉 Расскажи друзьям о квартирнике!",
        reply_markup=share_keyboard
    )
    await update.message.reply_text("Следить за новостями можно здесь: https://t.me/peterburgkvartirnik")

    return ConversationHandler.END

# Запуск бота
def main() -> None:
    application = import os

application = Application.builder().token(os.getenv("хуй")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_ACTION: [
                MessageHandler(filters.Regex("^Подать заявку$"), start_application),
                MessageHandler(filters.Regex("^Узнать подробнее$"), more_info),
                MessageHandler(filters.Regex("^Назад$"), start)
            ],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CHOOSE_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_genre)],
            ENTER_OTHER_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
            ENTER_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
            ENTER_REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_requirements)],
            ENTER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_application)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    keep_alive()
    application.run_polling()

if __name__ == "__main__":
    main()
