from flask import Flask, request
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import re
import os

app = Flask(__name__)

# Inisialisasi bot Telegram
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def get_url(vid_url):
    try:
        base_url = "https://facebook-video-downloader.fly.dev/deo.php"
        payload = {'url': vid_url}
        
        response = requests.post(base_url, data=payload)

        if response.status_code == 200:
            response_data = response.json()
            download_links = response_data.get("links", {})
            high_quality_link = download_links.get("Download High Quality")
            return high_quality_link
        else:
            print("Error: Unable to fetch data from the server.")
            return None

    except Exception as e:
        print(f"😴 Gagal mengambil data url: {e}")
        return None

@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    update = request.get_json()
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    
    if "text" in message:
        text = message["text"]
        nama = message["from"]["first_name"]
        if "last_name" in message["from"]:
            nama += ' ' + message["from"]["last_name"]

        if re.match(r'^[\/!\.]start', text, re.IGNORECASE):
            keyboard = [[InlineKeyboardButton("Support", url='https://telegraf.js.org/'),
                         InlineKeyboardButton("Dev", url='https://t.me/MzCoder')],
                        [InlineKeyboardButton("Update Channel", url='https://t.me/DutabotID')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id, f"Halo! {nama}, Saya adalah bot yang siap membantu Anda mendownload media dari facebook. Silakan kirim tautan facebook yang ingin Anda unduh, dan saya akan segera memulai proses pengunduhan", reply_markup=reply_markup, parse_mode='html')

        elif "facebook.com" in text or "fb.me" in text:
            urlfb = text.strip()
            bot.send_message(chat_id, "Mengirim File Harap Tunggu.!!")

            download_link = get_url(urlfb)

            if download_link:
                # Unduh video
                video_response = requests.get(download_link)
                video_filename = "downloaded_video.mp4"

                # Simpan video ke file
                with open(video_filename, 'wb') as video_file:
                    video_file.write(video_response.content)

                # Kirim video ke Telegram
                bot.send_video(chat_id, video_filename)

                # Hapus video setelah diupload
                os.remove(video_filename)

            else:
                bot.send_message(chat_id, "⚠️ Ada Yang Salah atau tidak dapat mengunduh video.")

        else:
            bot.send_message(chat_id, "Silakan kirim tautan Facebook yang valid.")

    return "OK", 200

if __name__ == '__main__':
    # Set webhook
    bot.start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
