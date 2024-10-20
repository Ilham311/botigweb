import requests
import os
from telethon import TelegramClient, events
from flask import Flask
import shutil
from threading import Thread
import asyncio

# Setup Flask
app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# Endpoint sederhana untuk pengalihan
@app.route('/')
def index():
    return '<h1>Selamat datang di Website Sederhana!</h1><p>Bot Telegram sedang berjalan di latar belakang...</p>'

# Menjalankan Flask server
def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# Fungsi untuk API Twitter
def twitter_api(twitter_url):
    url = 'https://twitter-downloader-download-twitter-videos-gifs-and-images.p.rapidapi.com/status'
    headers = {
        'x-rapidapi-key': '4f281a1be0msh5baa41ebeeda439p1d1139jsn3c26d05da8dd',
        'x-rapidapi-host': 'twitter-downloader-download-twitter-videos-gifs-and-images.p.rapidapi.com',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.10.0'
    }
    params = {'url': twitter_url}
    try:
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        variants = response_data['media']['video']['videoVariants']
        return next(v['url'] for v in variants if v['content_type'] == 'video/mp4')
    except Exception as e:
        print(e)
        return None

# Fungsi untuk API Instagram
def get_instagram_media(instagram_url):
    url = 'https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink'
    headers = {
        'x-rapidapi-key': 'da2822c5a9msh3665ef1bee3ad2cp1ab549jsn457a3b017e06',
        'x-rapidapi-host': 'auto-download-all-in-one.p.rapidapi.com',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.14.9'
    }
    data = {'url': instagram_url}
    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        return response_data['medias'][0]['url']
    except Exception as e:
        print(e)
        return None

# Fungsi untuk API Facebook
def get_facebook_video_url(fb_url):
    url = f'https://vdfr.aculix.net/fb?url={fb_url}'
    headers = {
        'Authorization': 'erg4t5hyj6u75u64y5ht4gf3er4gt5hy6uj7k8l9',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.12.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        media = response_data.get('media', [])
        return next((m['video_url'] for m in media if m['is_video']), None)
    except Exception as e:
        print(e)
        return None

# Fungsi untuk TikTok
def get_tiktok_play_url(tiktok_url):
    api_url = f'https://www.tikwm.com/api/?url={tiktok_url}'
    try:
        response = requests.get(api_url)
        response_data = response.json()
        return response_data['data']['play']
    except Exception as e:
        print(e)
        return None

# Fungsi untuk unduh dan unggah video
async def download_and_upload(event, video_url):
    if not video_url:
        await event.reply("Terjadi kesalahan saat mengambil URL video.")
        return

    await event.reply("Video berhasil diunduh. Sedang mengunggah...")
    try:
        response = requests.get(video_url, stream=True)
        file_path = './video.mp4'
        with open(file_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        await event.reply(file=file_path)
        os.remove(file_path)  # Hapus file setelah diunggah
    except Exception as e:
        print(e)
        await event.reply("Gagal mengunggah video.")

# Setup bot Telegram
api_id = 961780  # Ganti dengan API ID Telegram Anda
api_hash = 'bbbfa43f067e1e8e2fb41f334d32a6a7'
bot_token = '7375007973:AAEqgy2z2J2-Xii_wOhea98BmwMSdW82bHM'
client = TelegramClient('bot', api_id, api_hash)

# Menangani perintah unduh Instagram
@client.on(events.NewMessage(pattern='/ig'))
async def handle_instagram(event):
    try:
        url = event.message.text.split(' ')[1]  # Memeriksa apakah URL diberikan
        video_url = get_instagram_media(url)
        await download_and_upload(event, video_url)
    except IndexError:
        await event.reply("Silakan masukkan URL Instagram yang valid. Contoh: /ig <URL>")

# Menangani perintah unduh Facebook
@client.on(events.NewMessage(pattern='/fb'))
async def handle_facebook(event):
    try:
        url = event.message.text.split(' ')[1]  # Memeriksa apakah URL diberikan
        video_url = get_facebook_video_url(url)
        await download_and_upload(event, video_url)
    except IndexError:
        await event.reply("Silakan masukkan URL Facebook yang valid. Contoh: /fb <URL>")

# Menangani perintah unduh Twitter
@client.on(events.NewMessage(pattern='/tw'))
async def handle_twitter(event):
    try:
        url = event.message.text.split(' ')[1]  # Memeriksa apakah URL diberikan
        video_url = twitter_api(url)
        await download_and_upload(event, video_url)
    except IndexError:
        await event.reply("Silakan masukkan URL Twitter yang valid. Contoh: /tw <URL>")

# Menangani perintah unduh TikTok
@client.on(events.NewMessage(pattern='/tt'))
async def handle_tiktok(event):
    try:
        url = event.message.text.split(' ')[1]  # Memeriksa apakah URL diberikan
        video_url = get_tiktok_play_url(url)
        await download_and_upload(event, video_url)
    except IndexError:
        await event.reply("Silakan masukkan URL TikTok yang valid. Contoh: /tt <URL>")


# Fungsi untuk menjalankan bot Telegram
def run_bot():
    loop = asyncio.new_event_loop()  # Membuat event loop baru
    asyncio.set_event_loop(loop)  # Mengatur event loop di thread ini
    client.start()
    client.run_until_disconnected()

# Menjalankan Flask dan bot Telegram di thread terpisah
if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=run_bot).start()
