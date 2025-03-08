import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from nequi import nequi, nequi_a_nequi, nequi_a_comercio, name as nequi_name, number as nequi_number, amount as nequi_amount, cancel as nequi_cancel, comercio_name, comercio_amount
from bancolombia import bancol_a_nequi, number as bancol_number, amount as bancol_amount, cancel as bancol_cancel
from states import NEQUI_MENU, NEQUI_NAME, NEQUI_NUMBER, NEQUI_AMOUNT, NEQUI_COMERCIO_NAME, NEQUI_COMERCIO_AMOUNT, BANCOLOMBIA_NUMBER, BANCOLOMBIA_AMOUNT

TOKEN = os.getenv("7116486757:AAHpLB8iEZCPa4kFZft6jx_mBVwTmHz4eT8")
ADMIN_ID = 1415509092

user_keys = {
    6929246709: "$$$",
    1415509092: "yo"
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_keys:
        keyboard = [['Nequi', 'Bancol a Nequi']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)
        logger.info(f"Usuario {user_id} autorizado.")
    else:
        await update.message.reply_text("No tienes acceso. Solicítalo a @Bacbix.")
        logger.info(f"Usuario {user_id} sin acceso.")

async def send_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_keys and context.args:
        message = " ".join(context.args)
        for uid in user_keys:
            try:
                await context.bot.send_message(uid, message)
                logger.info(f"Mensaje enviado a {uid}")
            except Exception as e:
                logger.error(f"Error enviando mensaje a {uid}: {e}")
        await update.message.reply_text("Mensaje enviado.")
    else:
        await update.message.reply_text("No tienes acceso o falta el mensaje.")

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID and len(context.args) == 2:
        user_id, new_key = int(context.args[0]), context.args[1]
        user_keys[user_id] = new_key
        await update.message.reply_text(f"Clave {new_key} asignada a {user_id}.")
        logger.info(f"Clave {new_key} creada para {user_id}")
    else:
        await update.message.reply_text("Permiso denegado o argumentos inválidos.")

async def remove_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID and context.args:
        user_id = int(context.args[0])
        if user_id in user_keys:
            del user_keys[user_id]
            await update.message.reply_text(f"Clave eliminada para {user_id}.")
        else:
            await update.message.reply_text("Usuario no encontrado.")
    else:
        await update.message.reply_text("Permiso denegado o argumentos inválidos.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("msg", send_msg))
    application.add_handler(CommandHandler("create_key", create_key))
    application.add_handler(CommandHandler("removekey", remove_key))

    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ["PORT"]),
        url_path=TOKEN,
        webhook_url=f'https://{os.getenv("bacbox-68f7ccc5fd1b")}.herokuapp.com/{TOKEN}'
    )
