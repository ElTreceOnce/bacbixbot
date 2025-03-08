import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from nequi import nequi, nequi_a_nequi, nequi_a_comercio, name as nequi_name, number as nequi_number, amount as nequi_amount, cancel as nequi_cancel, comercio_name, comercio_amount
from bancolombia import bancol_a_nequi, number as bancol_number, amount as bancol_amount, cancel as bancol_cancel
from states import NEQUI_MENU, NEQUI_NAME, NEQUI_NUMBER, NEQUI_AMOUNT, NEQUI_COMERCIO_NAME, NEQUI_COMERCIO_AMOUNT, BANCOLOMBIA_NUMBER, BANCOLOMBIA_AMOUNT

# Obtiene el token del bot desde las variables de entorno
TOKEN = ("7116486757:AAHpLB8iEZCPa4kFZft6jx_mBVwTmHz4eT8")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# El ID del administrador que puede crear y eliminar claves
ADMIN_ID = 1415509092

# Diccionario manual con las claves de los usuarios
user_keys = {
    6929246709: "$$$",
    1415509092: "yo",
    # Agrega los usuarios que necesites con sus claves aquí
}

# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Comando /start recibido")
    
    # Verificar si el usuario tiene una clave válida
    user_id = update.message.from_user.id
    if user_id in user_keys:
        keyboard = [
            ['Nequi', 'Bancol a Nequi']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)
        logger.info(f"Usuario con ID {user_id} tiene acceso.")
    else:
        await update.message.reply_text("No tienes acceso. Solicítalo a @Bacbix.")
        logger.info(f"Usuario con ID {user_id} no tiene acceso.")

# Función para el comando /msg
async def send_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_keys:
        # Verificar si se proporciona un mensaje en los argumentos
        if context.args:
            message = " ".join(context.args)  # Unir todos los argumentos del mensaje
            # Enviar el mensaje a todos los usuarios en user_keys
            for uid in user_keys:
                try:
                    await context.bot.send_message(uid, message)
                    logger.info(f"Mensaje enviado a {uid}.")
                except Exception as e:
                    logger.error(f"No se pudo enviar mensaje a {uid}: {e}")
            await update.message.reply_text(f"Mensaje enviado a todos los usuarios.")
        else:
            await update.message.reply_text("Por favor, proporciona el mensaje a enviar.")
    else:
        await update.message.reply_text("No tienes acceso. Solicítalo a @Bacbix.")
        logger.info(f"Usuario con ID {user_id} no tiene acceso al comando /msg.")

# Función para crear una clave (solo admin)
async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID:
        if context.args:
            user_id = int(context.args[0])  # El ID del usuario a quien se le asignará la clave
            new_key = context.args[1]  # La clave que el admin quiere asignar
            user_keys[user_id] = new_key  # Asignar la clave al usuario
            await update.message.reply_text(f"Clave '{new_key}' generada y asignada al usuario {user_id}.")
            logger.info(f"Clave '{new_key}' generada y asignada al usuario {user_id} por el admin.")
        else:
            await update.message.reply_text("Por favor, proporciona el ID del usuario y la clave a asignar.")
    else:
        await update.message.reply_text("No tienes permisos para generar una clave.")
        logger.warning("Usuario sin permisos intentó generar una clave.")

# Función para eliminar una clave (solo admin)
async def remove_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID:
        if context.args:
            user_id = int(context.args[0])  # El ID del usuario cuya clave será eliminada
            if user_id in user_keys:
                del user_keys[user_id]  # Eliminar la clave del diccionario
                await update.message.reply_text(f"Clave del usuario {user_id} eliminada con éxito.")
                logger.info(f"Clave del usuario {user_id} eliminada por el admin.")
            else:
                await update.message.reply_text(f"El usuario {user_id} no tiene una clave asignada.")
        else:
            await update.message.reply_text("Por favor, proporciona el ID del usuario cuya clave deseas eliminar.")
    else:
        await update.message.reply_text("No tienes permisos para eliminar claves.")
        logger.warning("Usuario sin permisos intentó eliminar una clave.")

# Función para los comandos que requieren clave
async def command_with_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_keys:
        # Lógica para los comandos que se ejecutan solo si el usuario tiene una clave
        await update.message.reply_text(f"Comando ejecutado con éxito. Tu clave es {user_keys[user_id]}")
    else:
        await update.message.reply_text("No tienes acceso. Solicítalo a @Bacbix.")

if __name__ == '__main__':
    logger.info("Iniciando el bot")
    application = ApplicationBuilder().token(TOKEN).build()

    # Manejadores de comandos
    start_handler = CommandHandler('start', start)
    create_key_handler = CommandHandler('create_key', create_key)
    remove_key_handler = CommandHandler('removekey', remove_key)
    command_handler = CommandHandler('command_with_key', command_with_key)
    send_msg_handler = CommandHandler('msg', send_msg)

    # Conversación para el flujo de Nequi
    conv_handler_nequi = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Nequi$'), nequi)],
        states={
            NEQUI_MENU: [
                MessageHandler(filters.Regex('^Nequi a Nequi$'), nequi_a_nequi),
                MessageHandler(filters.Regex('^Nequi a Comercio$'), nequi_a_comercio),
            ],
            NEQUI_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_name)],
            NEQUI_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_number)],
            NEQUI_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_amount)],
            NEQUI_COMERCIO_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, comercio_name)],
            NEQUI_COMERCIO_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comercio_amount)],
        },
        fallbacks=[CommandHandler('cancel', nequi_cancel)],
        allow_reentry=True
    )

    # Conversación para el flujo de Bancol a Nequi
    conv_handler_bancolombia = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Bancol a Nequi$'), bancol_a_nequi)],
        states={
            BANCOLOMBIA_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_number)],
            BANCOLOMBIA_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_amount)],
        },
        fallbacks=[CommandHandler('cancel', bancol_cancel)],
        allow_reentry=True
    )

    # Añadir los manejadores de comandos y conversaciones
    application.add_handler(start_handler)
    application.add_handler(create_key_handler)
    application.add_handler(remove_key_handler)
    application.add_handler(command_handler)
    application.add_handler(send_msg_handler)
    application.add_handler(conv_handler_nequi)
    application.add_handler(conv_handler_bancolombia)

    # Iniciar el webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', '8443')),
        url_path=TOKEN,
        webhook_url=f'https://bacbox-68f7ccc5fd1b.herokuapp.com/{TOKEN}'
    )
