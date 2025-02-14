import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime
import os
from states import NEQUI_MENU, NEQUI_NAME, NEQUI_NUMBER, NEQUI_AMOUNT, NEQUI_COMERCIO_NAME, NEQUI_COMERCIO_AMOUNT
import pytz

logger = logging.getLogger(__name__)

# Obtén el directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas a imágenes y fuentes
IMAGE_DIR = os.path.join(BASE_DIR, 'img')
FONT_DIR = os.path.join(BASE_DIR, 'fonts')

async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Nequi option selected")
    keyboard = [
        ['Nequi a Nequi', 'Nequi a Comercio']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Selecciona una opción:', reply_markup=reply_markup)
    return NEQUI_MENU

async def nequi_a_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Nequi a Nequi selected")
    await update.message.reply_text('Por favor, introduce tu nombre:')
    return NEQUI_NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Name received")
    context.user_data['name'] = update.message.text.title()  # Convertir solo las iniciales a mayúsculas
    await update.message.reply_text('Por favor, introduce tu número:')
    return NEQUI_NUMBER

async def number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Number received")
    context.user_data['number'] = update.message.text
    await update.message.reply_text('Por favor, introduce la cantidad:')
    return NEQUI_AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Amount received")
    context.user_data['amount'] = update.message.text

    # Generar referencia
    context.user_data['reference'] = f"M{random.randint(10000000, 15000000)}"
    
    # Define la zona horaria de Colombia
    colombia_tz = pytz.timezone('America/Bogota')

    # Obtén la hora actual en la zona horaria de Colombia
    now = datetime.now(colombia_tz)

    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    day = now.day
    current_datetime = now.strftime(f'{day} de {months[now.month - 1]} de %Y, %I:%M %p').lower().replace('am', 'a. m.').replace('pm', 'p. m.')
    context.user_data['datetime'] = current_datetime

    # Aquí se manipula la imagen
    image_path = os.path.join(IMAGE_DIR, 'nequinuevo.jpg')
    font_path = os.path.join(FONT_DIR, 'Nesquic.ttf')s
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 47)

    # Características del texto
    name_color = (26, 3, 28)
    name_position = (50, 200)
    reference_position = (95, 690)
    number_position = (95, 874)
    datetime_position = (95, 1055)
    amount_position = (95, 1238)
    amount_small_position = (233, 1545)
    amount_small_color = (135, 135, 135)
    amount_small_font = ImageFont.truetype(font_path, 45)
    amount_cents_font = ImageFont.truetype(font_path, 35)

    name = context.user_data['name']
    reference = context.user_data['reference']
    number = context.user_data['number']
    amount = context.user_data['amount']

    # Formatear la cantidad
    amount_formatted = f"$ {int(amount):,}".replace(",", ".") + ",00"

    def draw_text(draw, position, text, font, color, vertical_scale=1.05):
        text_image = Image.new('RGBA', draw.textbbox((0, 0), text, font=font)[2:])
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((0, 0), text, font=font, fill=color)
        text_image = text_image.resize((text_image.width, int(text_image.height * vertical_scale)), Image.Resampling.LANCZOS)
        img.paste(text_image, position, text_image)

    draw_text(draw, name_position, name, font, name_color)
    draw_text(draw, reference_position, reference, font, name_color)
    draw_text(draw, number_position, number, font, name_color)
    draw_text(draw, datetime_position, current_datetime, font, name_color)
    draw_text(draw, amount_position, amount_formatted, font, name_color, vertical_scale=1.1)

    # Dibujar la cantidad pequeña en dos partes
    amount_without_cents = f"$ {int(amount):,}".replace(",", ".")
    draw_text(draw, amount_small_position, amount_without_cents, amount_small_font, amount_small_color)
    
    amount_without_cents_width = draw.textbbox((0, 0), amount_without_cents, font=amount_small_font)[2]
    draw_text(draw, (amount_small_position[0] + amount_without_cents_width, amount_small_position[1] + 8), ",00", amount_cents_font, amount_small_color, vertical_scale=1.1)

    output_path = os.path.join(IMAGE_DIR, 'nequiclear_output.png')

    # Guardar la imagen sin reducir sus dimensiones ni calidad
    img.save(output_path, 'PNG')

    # Enviar la imagen generada al usuario
    with open(output_path, 'rb') as photo:
        await update.message.reply_document(document=photo, caption=f"Comprobante generado con éxito.")

    # Agregar botón de "Reintentar"
    keyboard = [
        ['/start']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('¿Deseas generar otro comprobante?', reply_markup=reply_markup)
    
    # Redirigir al comando `/start` para que el flujo se reinicie correctamente
    return ConversationHandler.END

async def nequi_a_comercio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Nequi a Comercio selected")
    await update.message.reply_text('Por favor, introduce el nombre del comercio:')
    return NEQUI_COMERCIO_NAME

async def comercio_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Comercio Name received")
    # Convertir solo las iniciales a mayúsculas
    context.user_data['comercio_name'] = update.message.text.title()  
    await update.message.reply_text('Por favor, introduce la cantidad:')
    return NEQUI_COMERCIO_AMOUNT

async def comercio_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Comercio Amount received")
    context.user_data['comercio_amount'] = update.message.text

    # Generar referencia
    reference = f"M{random.randint(5000000, 7000000)}"
    

    # Define la zona horaria de Colombia
    colombia_tz = pytz.timezone('America/Bogota')


    # Obtén la hora actual en la zona horaria de Colombia
    now = datetime.now(colombia_tz)

    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    day = now.day
    month = months[now.month - 1]
    year = now.year
    time = now.strftime('%I:%M %p').lower().replace('am', 'a. m.').replace('pm', 'p. m.')
    current_datetime = f'{day:02d} de {month} de {year} a las {time}'

    # Aquí se manipula la imagen
    image_path = os.path.join(IMAGE_DIR, 'nesquikqr.png')  # Nueva imagen para comercio
    font_path = os.path.join(FONT_DIR, 'Nesquic.ttf')  # Cambia esto al path correcto de tu fuente
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 220)

    # Características del texto
    name_color = (26, 3, 28)
    comercio_position = (393, 4570)
    amount_position = (393, 5300)
    datetime_position = (393, 6070)
    reference_position = (393, 6870)

    comercio_name = context.user_data['comercio_name']
    comercio_amount = f"$ {int(context.user_data['comercio_amount']):,}".replace(",", ".") + ",00"

    # Dibujar los textos en la imagen
    draw.text(comercio_position, comercio_name, font=font, fill=name_color)
    draw.text(amount_position, comercio_amount, font=font, fill=name_color)
    draw.text(datetime_position, current_datetime, font=font, fill=name_color)
    draw.text(reference_position, reference, font=font, fill=name_color)

    output_path = 'C:\\Users\\MARTIN ORTEGA\\Desktop\\botnesquik\\img\\nesquikqr_output.png'

    # Guardar la imagen
    img.save(output_path, 'PNG')

    # Enviar la imagen generada
    with open(output_path, 'rb') as photo:
        await update.message.reply_document(document=photo, caption=f'Comprobante generado con éxito')

            # Agregar botón de "Reintentar" que redirige a /start
    keyboard = [
        ['/start']  # Este botón redirige directamente al comando /start
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('¿Deseas generar otro comprobante?', reply_markup=reply_markup)
    
    # Finalizar la conversación ya que el usuario ahora será redirigido al flujo inicial
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Operation cancelled")
    await update.message.reply_text('Operación cancelada.')
    return ConversationHandler.END
