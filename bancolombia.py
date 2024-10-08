import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime
import os
import pytz
from states import BANCOLOMBIA_NUMBER, BANCOLOMBIA_AMOUNT

logger = logging.getLogger(__name__)

# Configurar rutas basadas en la variable de entorno o usar un directorio relativo
BASE_DIR = os.getenv('BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, 'img')
FONT_DIR = os.path.join(BASE_DIR, 'fonts')

async def bancol_a_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Bancol a Nequi selected")
    await update.message.reply_text('Por favor, introduce el número:')
    return BANCOLOMBIA_NUMBER

async def number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Number received")
    context.user_data['number'] = update.message.text
    await update.message.reply_text('Por favor, introduce la cantidad:')
    return BANCOLOMBIA_AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Amount received")
    # Formatear la cantidad
    amount = int(update.message.text.replace(".", ""))
    context.user_data['amount'] = f"$ {amount:,}".replace(",", ".")

    # Generar los textos
    comprobante_no = f"Comprobante No. {random.randint(10000, 99999):010d}"
    
    # Define la zona horaria de Colombia
    colombia_tz = pytz.timezone('America/Bogota')

    # Obtén la hora actual en la zona horaria de Colombia
    now = datetime.now(colombia_tz)

    # Formatea la fecha y hora
    fecha_actual = now.strftime('%d %b %Y - %I:%M %p').upper().replace('AM', 'a.m.').replace('PM', 'p.m.')

    # Traducción de meses al español
    meses = {
        "JAN": "Ene", "FEB": "Feb", "MAR": "Mar", "APR": "Abr",
        "MAY": "May", "JUN": "Jun", "JUL": "Jul", "AUG": "Ago",
        "SEP": "Sep", "OCT": "Oct", "NOV": "Nov", "DEC": "Dic"
    }

    # Reemplaza los meses en inglés con los equivalentes en español
    for eng, esp in meses.items():
        fecha_actual = fecha_actual.replace(eng, esp)

    numero_aleatorio = f"*{random.randint(1000, 9999)}"
    numero_usuario = context.user_data['number']
    cantidad_usuario = context.user_data['amount']

    # Cargar la imagen del comprobante
    image_path = os.path.join(IMAGE_DIR, 'bancolnequi.png')
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Configurar las fuentes
    font_path_1 = os.path.join(FONT_DIR, 'OpenSans-Regular.ttf')
    font_path_2 = os.path.join(FONT_DIR, 'avrile-sans.medium.ttf')
    font_1 = ImageFont.truetype(font_path_1, 175)
    font_2 = ImageFont.truetype(font_path_2, 215)

    # Colores de texto
    color_texto = "#2C2A29"

    # Posiciones del texto
    positions = [
        (1227, 2555),  # Posición para el Comprobante No
        (1480, 2870),  # Posición para la fecha
        (390, 4370),   # Posición para el número aleatorio
        (390, 5450),   # Posición para el número de usuario
        (390, 6200)    # Posición para la cantidad
    ]

    # Dibujar los textos en la imagen
    draw.text(positions[0], comprobante_no, font=font_1, fill=color_texto)
    draw.text(positions[1], fecha_actual, font=font_1, fill="black")
    draw.text(positions[2], numero_aleatorio, font=font_2, fill=color_texto)
    draw.text(positions[3], numero_usuario, font=font_2, fill=color_texto)
    draw.text(positions[4], cantidad_usuario, font=font_2, fill=color_texto)

    # Guardar la imagen modificada
    output_path = os.path.join(IMAGE_DIR, 'bancolnequi_output.png')
    img.save(output_path)

    # Enviar la imagen generada al usuario
    with open(output_path, 'rb') as photo:
        await update.message.reply_document(document=photo, caption="Comprobante generado con éxito.")
    
    # Agregar botón de "Reintentar"
    keyboard = [
        ['/start']  # Este botón redirige al comando /start para comenzar de nuevo
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('¿Deseas generar otro comprobante?', reply_markup=reply_markup)

    # Retornar al menú principal para seleccionar otra opción
    return ConversationHandler.END

# Función para cancelar la operación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Operation cancelled")
    await update.message.reply_text('Operación cancelada.')
    return ConversationHandler.END
