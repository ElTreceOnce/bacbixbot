import logging
import os
import random
import string
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

# El ID del administrador que puede crear claves
ADMIN_ID = 1415509092

# Diccionario para almacenar las claves de los usuarios
user_keys = {}

# Función para crear una clave aleatoria
def generate_key() -> str:
    length = 16  # Longitud de la clave
    characters = string.ascii_letters + string.digits  # Letras y números
    key = ''.join(random.choice(characters) for _ in range(length))
    return key

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
        await update.message.reply_text("No tienes acceso. Solicitalo a @Bacbix.")
        logger.info(f"Usuario con ID {user_id} no tiene acceso.")

# Función para crear una clave (solo admin)
async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID:
        if context.args:
            user_id = int(context.args[0])  # El ID del usuario a quien se le asignará la clave
            new_key = generate_key()  # Generar una nueva clave
            user_keys[user_id] = new_key  # Asignar la clave al usuario
            await update.message.reply_text(f"Clave generada y asignada al usuario {user_id}: {new_key}")
            logger.info(f"Clave generada y asignada al usuario {user_id} por el admin.")
        else:
            await update.message.reply_text("Por favor, proporciona el ID del usuario al que se le asignará la clave.")
    else:
        await update.message.reply_text("No tienes permisos para generar una clave.")
        logger.warning("Usuario sin permisos intentó generar una clave")

# Función para eliminar una clave (solo admin)
async def remove_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID:
        if context.args:
            user_id = int(context.args[0])  # El ID del usuario cuya clave será eliminada
            if user_id in user_keys:
                del user_keys[user_id]  # Eliminar la clave del usuario
                await update.message.reply_text(f"Clave eliminada para el usuario {user_id}.")
                logger.info(f"Clave eliminada para el usuario {user_id} por el admin.")
            else:
                await update.message.reply_text(f"El usuario {user_id} no tiene una clave registrada.")
                logger.warning(f"Intento de eliminar una clave para un usuario no registrado: {user_id}.")
        else:
            await update.message.reply_text("Por favor, proporciona el ID del usuario cuya clave deseas eliminar.")
    else:
        await update.message.reply_text("No tienes permisos para eliminar una clave.")
        logger.warning("Usuario sin permisos intentó eliminar una clave.")

# Función para los comandos que requieren clave
async def command_with_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_keys:
        # Lógica para los comandos que se ejecutan solo si el usuario tiene una clave
        await update.message.reply_text(f"Comando ejecutado con éxito. Tu clave es {user_keys[user_id]}")
    else:
        await update.message.reply_text("No tienes acceso. Solicitalo a @Bacbix.")

if __name__ == '__main__':
    logger.info("Iniciando el bot")
    application = ApplicationBuilder().token(TOKEN).build()

    # Manejador para el comando /start
    start_handler = CommandHandler('start', start)

    # Manejador para el comando /create_key (solo admin)
    create_key_handler = CommandHandler('create_key', create_key)

    # Manejador para los comandos con clave
    command_handler = CommandHandler('command_with_key', command_with_key)

    # Manejador para el comando /remove_key (solo admin)
    remove_key_handler = CommandHandler('remove_key', remove_key)

    # Conversación para el flujo de Nequi
    conv_handler_nequi = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Nequi$'), nequi)],  # Aquí estamos capturando la opción 'Nequi'
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
        allow_reentry=True  # Esto permite que el flujo se reinicie si se vuelve a seleccionar 'Nequi'
    )

    # Conversación para el flujo de Bancol a Nequi
    conv_handler_bancolombia = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Bancol a Nequi$'), bancol_a_nequi)],  # Entrada cuando seleccionan 'Bancol a Nequi'
        states={
            BANCOLOMBIA_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_number)],
            BANCOLOMBIA_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_amount)],
        },
        fallbacks=[CommandHandler('cancel', bancol_cancel)],
        allow_reentry=True  # Esto permite que el flujo se reinicie si se vuelve a seleccionar 'Bancol a Nequi'
    )

    # Añadir los manejadores de comandos y conversaciones
    application.add_handler(start_handler)
    application.add_handler(create_key_handler)  # Agregar el manejador para el comando /create_key
    application.add_handler(command_handler)  # Agregar el manejador para los comandos con clave
    application.add_handler(conv_handler_nequi)
    application.add_handler(conv_handler_bancolombia)

    # Iniciar el webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', '8443')),
        url_path=TOKEN,
        webhook_url=f'https://bacbix-10b478738eaf.herokuapp.com/{TOKEN}'
    )
