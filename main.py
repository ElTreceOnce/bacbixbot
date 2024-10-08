import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from nequi import nequi, nequi_a_nequi, nequi_a_comercio, name as nequi_name, number as nequi_number, amount as nequi_amount, cancel as nequi_cancel, comercio_name, comercio_amount
from bancolombia import bancol_a_nequi, number as bancol_number, amount as bancol_amount, cancel as bancol_cancel
from states import NEQUI_MENU, NEQUI_NAME, NEQUI_NUMBER, NEQUI_AMOUNT, NEQUI_COMERCIO_NAME, NEQUI_COMERCIO_AMOUNT, BANCOLOMBIA_NUMBER, BANCOLOMBIA_AMOUNT

TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Función inicial para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Start command received")
    
    # Aquí se crean los dos botones: 'Nequi' y 'Bancol a Nequi'
    keyboard = [
        ['Nequi', 'Bancol a Nequi']
    ]
    
    # Se agrega el teclado con los botones al mensaje de bienvenida
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)

if __name__ == '__main__':
    logger.info("Starting bot")
    application = ApplicationBuilder().token(TOKEN).build()

    # Manejador para el comando /start
    start_handler = CommandHandler('start', start)

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
    )

    # Conversación para el flujo de Bancol a Nequi
    conv_handler_bancolombia = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Bancol a Nequi$'), bancol_a_nequi)],  # Entrada cuando seleccionan 'Bancol a Nequi'
        states={
            BANCOLOMBIA_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_number)],
            BANCOLOMBIA_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bancol_amount)],
        },
        fallbacks=[CommandHandler('cancel', bancol_cancel)],
    )

    # Añadir los manejadores de comandos y conversaciones
    application.add_handler(start_handler)
    application.add_handler(conv_handler_nequi)
    application.add_handler(conv_handler_bancolombia)

    # Iniciar el webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', '8443')),
        url_path=TOKEN,
        webhook_url=f'https://botnesquik-0d8ca37e275c.herokuapp.com/{TOKEN}'
    )
