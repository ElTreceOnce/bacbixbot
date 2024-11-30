import logging
import os
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from nequi import nequi, nequi_a_nequi, nequi_a_comercio, name as nequi_name, number as nequi_number, amount as nequi_amount, cancel as nequi_cancel, comercio_name, comercio_amount
from bancolombia import bancol_a_nequi, number as bancol_number, amount as bancol_amount, cancel as bancol_cancel

# Archivo de claves
KEYS_FILE = "keys.js"

# ID del administrador
ADMIN_ID = 1415509092  # Este es el ID del admin que puede asignar claves

# Cargar claves desde el archivo .js
def load_keys():
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "w") as f:
            f.write("const keys = [];\nmodule.exports = keys;")
    with open(KEYS_FILE, "r") as f:
        content = f.read().replace("const keys = ", "").replace(";\nmodule.exports = keys;", "")
        return json.loads(content) if content.strip() else []

# Guardar claves en el archivo .js
def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        f.write("const keys = ")
        f.write(json.dumps(keys, indent=4))
        f.write(";\nmodule.exports = keys;")

# Generar una clave única
def generate_key(user_id: int) -> str:
    keys = load_keys()
    expiration_date = datetime.now() + timedelta(days=30)
    new_key = f"KEY-{user_id}-{int(datetime.now().timestamp())}"
    keys.append({
        "key": new_key,
        "user_id": user_id,
        "expiration_date": expiration_date.isoformat()
    })
    save_keys(keys)
    return new_key

# Validar si una clave es válida
def is_key_valid(user_id: int) -> bool:
    keys = load_keys()
    for key in keys:
        if key["user_id"] == user_id:
            expiration_date = datetime.fromisoformat(key["expiration_date"])
            return expiration_date > datetime.now()
    return False

# Comando para generar claves (solo para el administrador)
async def generate_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == ADMIN_ID:  # Verifica que el usuario sea el administrador
        if len(context.args) != 1:
            await update.message.reply_text("Uso: /generatekey <user_id>")
            return
        try:
            user_id = int(context.args[0])
            new_key = generate_key(user_id)
            await update.message.reply_text(f"Clave generada para el usuario {user_id}: {new_key}")
        except Exception as e:
            await update.message.reply_text(f"Error generando clave: {e}")
    else:
        await update.message.reply_text("No tienes permisos para usar este comando.")

# Función inicial para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_key_valid(user_id):
        # Aquí se crean los dos botones: 'Nequi' y 'Bancol a Nequi'
        keyboard = [
            ['Nequi', 'Bancol a Nequi']
        ]
        # Se agrega el teclado con los botones al mensaje de bienvenida
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)
    else:
        await update.message.reply_text("No tienes una clave válida. Contacta a @Bacbix para obtener acceso.")

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

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    TOKEN = "7116486757:AAHpLB8iEZCPa4kFZft6jx_mBVwTmHz4eT8"
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('generatekey', generate_key_command))
    application.add_handler(conv_handler_nequi)
    application.add_handler(conv_handler_bancolombia)

    # Iniciar el webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', '8443')),
        url_path=TOKEN,
        webhook_url=f'https://bacbix-10b478738eaf.herokuapp.com/{TOKEN}'
    )
