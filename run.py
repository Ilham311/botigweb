import os
import requests
import shutil
from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web
import logging

# Bot token dari Telegram
BOT_TOKEN = '7375007973:AAEqgy2z2J2-Xii_wOhea98BmwMSdW82bHM'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Fungsi untuk API Twitter
async def twitter_api(twitter_url):
    url = 'https://twitter-downloader-download-twitter-videos-gifs-and-images.p.rapidapi.com/status'
    headers = {
        'x-rapidapi-key': '4f281a1be0msh5baa41ebeeda439p1d1139jsn3c26d05da8dd',
        'x-rapidapi-host': 'twitter-downloader-download-twitter-videos-gifs-and-images.p.rapidapi.com',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.10.0'
    }
    try:
        response = requests.get(url, params={'url': twitter_url}, headers=headers)
        response.raise_for_status()
        variants = response.json()['media']['video']['videoVariants']
        return next(v['url'] for v in variants if v['content_type'] == 'video/mp4')
    except Exception as e:
        logging.error(f"Error fetching Twitter video: {e}")
        return None

# Fungsi untuk API Instagram
async def get_instagram_media(instagram_url):
    url = 'https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink'
    headers = {
        'x-rapidapi-key': 'da2822c5a9msh3665ef1bee3ad2cp1ab549jsn457a3b017e06',
        'x-rapidapi-host': 'auto-download-all-in-one.p.rapidapi.com',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.14.9'
    }
    try:
        response = requests.post(url, json={'url': instagram_url}, headers=headers)
        response.raise_for_status()
        return response.json()['medias'][0]['url']
    except Exception as e:
        logging.error(f"Error fetching Instagram media: {e}")
        return None

# Fungsi untuk API Facebook
async def get_facebook_video_url(fb_url):
    url = f'https://vdfr.aculix.net/fb?url={fb_url}'
    headers = {
        'Authorization': 'erg4t5hyj6u75u64y5ht4gf3er4gt5hy6uj7k8l9',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.12.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media = response.json()['media']
        return media[0]['video_url'] if media and media[0]['is_video'] else None
    except Exception as e:
        logging.error(f"Error fetching Facebook video: {e}")
        return None

# Fungsi untuk TikTok
async def get_tiktok_play_url(tiktok_url):
    api_url = f'https://www.tikwm.com/api/?url={tiktok_url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()['data']['play']
    except Exception as e:
        logging.error(f"Error fetching TikTok video: {e}")
        return None

# Fungsi untuk unduh dan unggah video
async def download_and_upload(message: types.Message, video_url: str):
    if not video_url:
        await message.answer("Terjadi kesalahan saat mengambil URL video.")
        return

    try:
        file_path = 'video.mp4'
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        await message.answer_video(types.InputFile(file_path))
        os.remove(file_path)  # Hapus file setelah diunggah
    except Exception as e:
        logging.error(f"Error during download/upload: {e}")
        await message.answer("Gagal mengunggah video.")

# Fungsi handler platform
async def handle_instagram(message: types.Message, url: str):
    video_url = await get_instagram_media(url)
    await download_and_upload(message, video_url)

async def handle_facebook(message: types.Message, url: str):
    video_url = await get_facebook_video_url(url)
    await download_and_upload(message, video_url)

async def handle_twitter(message: types.Message, url: str):
    video_url = await twitter_api(url)
    await download_and_upload(message, video_url)

async def handle_tiktok(message: types.Message, url: str):
    video_url = await get_tiktok_play_url(url)
    await download_and_upload(message, video_url)

# Handler untuk perintah unduh
@dp.message_handler(commands=['ig', 'fb', 'tw', 'tt'])
async def download_video(message: types.Message):
    text = message.text.split(' ')
    command = text[0]
    url = text[1] if len(text) > 1 else None

    if not url:
        await message.answer("URL tidak valid. Silakan coba lagi.")
        return

    if command == '/ig':
        await handle_instagram(message, url)
    elif command == '/fb':
        await handle_facebook(message, url)
    elif command == '/tw':
        await handle_twitter(message, url)
    elif command == '/tt':
        await handle_tiktok(message, url)
    else:
        await message.answer("Perintah tidak valid.")

# Fungsi untuk menjalankan bot
async def on_startup(dp):
    logging.info("Bot sedang berjalan...")

if __name__ == '__main__':
    from aiogram.utils.executor import start_polling
    start_polling(dp, on_startup=on_startup)

# Setup Express Web Server
async def handle_index(request):
    return web.Response(text="<h1>Selamat datang di Website Sederhana!</h1><p>Bot Telegram sedang berjalan di latar belakang...</p>", content_type='text/html')

app = web.Application()
app.router.add_get('/', handle_index)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    web.run_app(app, port=os.getenv('PORT', 3000))
