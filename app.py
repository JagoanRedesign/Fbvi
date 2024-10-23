from flask import Flask, request
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import re
import os
import asyncio

app = Flask(__name__)

# Inisialisasi bot Telegram
api_id = "25316442"  # Ganti dengan API ID Anda
api_hash = "39b99470938f7b377f1928c10f848944"  # Ganti dengan API Hash Anda
bot_token = "6513065243:AAG9pKG8ycUV3aHk-72oZ0_FrAWD7ed3tRQ"  # Ganti dengan Token Bot Anda

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def get_url(vid_url):
    try:
        base_url = "https://facebook-video-downloader.fly.dev/app/main.php"
        payload = {'url': vid_url}
        
        response = requests.post(base_url, data=payload)
        print(f"Response status code: {response.status_code}")  # Log status kode

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

@bot.on_message(filters.text)
async def handle_text(client, message):
    print(f"Received message: {message.text}")  # Log pesan yang diterima
    chat_id = message.chat.id
    text = message.text
    nama = message.from_user.first_name
    if message.from_user.last_name:
        nama += ' ' + message.from_user.last_name

    if re.match(r'^[\/!\.]start', text, re.IGNORECASE):
        keyboard = [[InlineKeyboardButton("Support", url='https://telegraf.js.org/'),
                     InlineKeyboardButton("Dev", url='https://t.me/MzCoder')],
                    [InlineKeyboardButton("Update Channel", url='https://t.me/DutabotID')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id, f"Halo! {nama}, Saya adalah bot yang siap membantu Anda mendownload media dari Facebook. Silakan kirim tautan Facebook yang ingin Anda unduh, dan saya akan segera memulai proses pengunduhan.", reply_markup=reply_markup, parse_mode='html')

    elif "facebook.com" in text or "fb.me" in text:
        urlfb = text.strip()
        await bot.send_message(chat_id, "Mengirim File Harap Tunggu.!!")

        download_link = get_url(urlfb)

        if download_link:
            print(f"Download link: {download_link}")  # Log tautan unduhan
            # Unduh video
            video_response = requests.get(download_link)
            video_filename = "downloaded_video.mp4"

            # Simpan video ke file
            with open(video_filename, 'wb') as video_file:
                video_file.write(video_response.content)

            # Kirim video ke Telegram
            await bot.send_video(chat_id, video_filename)

            # Hapus video setelah diupload
            os.remove(video_filename)

        else:
            await bot.send_message(chat_id, "⚠️ Ada Yang Salah atau tidak dapat mengunduh video.")

    else:
        await bot.send_message(chat_id, "Silakan kirim tautan Facebook yang valid.")

@app.route("/", methods=["GET"])
def ping():
    return "Bot is running!", 200

async def run_bot():
    await bot.start()
    await bot.idle()  # Menunggu sampai bot dihentikan

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Jalankan bot di event loop utama
    loop.create_task(run_bot())

    # Jalankan aplikasi Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
