import telebot
import os
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from tqdm import tqdm   
import io
import logging

# Add import for os.path
import os.path

#Conexion con bot
TOKEN = '7078219972:AAGAMi37OKY52dgn8wh54nMDi8Emnjg2ewQ'
bot = telebot.TeleBot(TOKEN)

UPLOAD_FOLDER = 'pdf/'
OUTPUT_FOLDER = 'txt/'  # Define the output folder for text files

# Crear la carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check if the output folder exists, if not, create it
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

#creacion de comandos
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hola!, Soy Lay, enviame el archivo a convertir en OCR usando /sendpdf')

@bot.message_handler(commands=['sendpdf'])
def send_pdf_prompt(message):
    bot.reply_to(message, 'Por favor, envía el archivo PDF.')

# Manejar archivos recibidos
@bot.message_handler(content_types=['document'])
def handle_pdf(message):
    try:
        # Guardar el archivo en la carpeta de carga
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        # Responder con el nombre del archivo recibido
        bot.reply_to(message, f'Se recibió el archivo PDF: {message.document.file_name}')
        bot.reply_to(message, f'Procesando...')

        # Perform OCR and save text to file
        file_name = os.path.splitext(message.document.file_name)[0]  # Extract file name without extension
        pdf_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
        output_file = file_name + ".txt"
        output_file_full_path = os.path.join(OUTPUT_FOLDER, output_file)

        # Check if the PDF file exists
        if not os.path.isfile(pdf_path):
            bot.reply_to(message, "Invalid PDF file path.")
            return
        
        # Extract text from PDF
        text = pdf_to_text(pdf_path)

        # Write OCR text to file
        write_ocr_text_to_file(text, output_file_full_path)

        # Send response with extracted text
        bot.reply_to(message, "Text extracted from PDF:")
        # send_text_in_chunks(text, message.chat.id)
        # Send response with text file attachment
        bot.send_document(message.chat.id, open(output_file_full_path, 'rb'))
        # Send response with text file attachment
        #send_text_or_file_in_chunks(output_file_full_path, message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error: {e}")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 'Puedes interactuar conmigo usando comandos, Por Ahora, solo respondo a /start y /send_pdf')

# Esta función responde a cualquier mensaje que no sea un comando ni un archivo
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, 'No entiendo ese comando. Por favor, usa /start o /help para obtener ayuda.')

# Function to send text or file in chunks
def send_text_or_file_in_chunks(file_path, chat_id):
    chunk_size = 4096  # Maximum message length supported by Telegram
    if os.path.getsize(file_path) <= chunk_size:
        # If file size is within the limit, send it as a document
        bot.send_document(chat_id, open(file_path, 'rb'))
    else:
        # If file size exceeds the limit, send text in chunks
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            for i in range(0, len(text), chunk_size):
                bot.send_message(chat_id, text[i:i + chunk_size])

# Function to extract images from PDF
def extract_images_from_pdf(pdf_bytes):
    images = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for image in page.images:
                images.append(image.to_image())
    return images

# Function to convert images to text using OCR
def image_to_text(image):
    text = pytesseract.image_to_string(image, lang='spa', config='--oem 1 --psm 3')
    return text

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page_num, page in enumerate(tqdm(pages, desc="Extracting text", unit="page")):
        # text += f"Page {page_num + 1}:\n"
        text += image_to_text(page)
        text += "\n\n"
    return text

def write_ocr_text_to_file(text, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"OCR text saved to {output_file}")
    except Exception as e:
        print(f"Failed to save OCR text to {output_file}: {e}")

# Function to send text in chunks
def send_text_in_chunks(text, chat_id):
    chunk_size = 4096  # Maximum message length supported by Telegram
    for i in range(0, len(text), chunk_size):
        bot.send_message(chat_id, text[i:i+chunk_size])


if __name__ == "__main__":
    bot.polling(none_stop=True)
