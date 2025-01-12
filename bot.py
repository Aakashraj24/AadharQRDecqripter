import telebot
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import json
import os

# Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Aadhaar QR decode function
def decode_aadhaar_qr(image_path):
    img = cv2.imread(image_path)
    qr_codes = decode(img)
    if qr_codes:
        qr_data = qr_codes[0].data.decode("utf-8")
        try:
            # Try converting to JSON format
            json_data = json.loads(qr_data)
            return json_data
        except json.JSONDecodeError:
            return {"error": "QR code data is not in valid JSON format"}
    return {"error": "No QR code detected"}

# Handle image messages
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Download the image
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = f"{message.photo[-1].file_id}.jpg"
        
        # Save the image
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Decode the QR code
        result = decode_aadhaar_qr(image_path)

        # Create JSON file from result
        json_file_path = f"{message.photo[-1].file_id}.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)
        
        # Send the JSON file to the user
        with open(json_file_path, 'rb') as json_file:
            bot.send_document(message.chat.id, json_file)
        
        # Clean up files (image and JSON)
        os.remove(image_path)
        os.remove(json_file_path)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Start the bot
print("Bot is running...")
bot.polling()
