import logging
import os
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

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

# Verificación de clave al inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_key_valid(user_id):
        keyboard = [['Nequi', 'Bancol a Nequi']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)
    else:
        await update.message.reply_text("No tienes una clave válida. Contacta a @Bacbix para obtener acceso.")

# Configuración del bot
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    TOKEN = "7116486757:AAHpLB8iEZCPa4kFZft6jx_mBVwTmHz4eT8"
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('generatekey', generate_key_command))

    application.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', '8443')),
        url_path=TOKEN,
        webhook_url=f'https://bacbix-10b478738eaf.herokuapp.com/{TOKEN}'
    )
