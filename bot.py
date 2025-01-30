import os
import asyncio
import aiohttp
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 Bot Credentials
API_ID = "29201763"
API_HASH = "10d0e463862b3d0e4c2441aa70b73c8f"
BOT_TOKEN = "7479227005:AAEHDWOhE6HI4y2MFzk14vVtoMZ_2oOV3_w"

# 🔹 Target Telegram Channel for Uploads
TARGET_CHANNEL = "@koh_premium_bots"

# 🔹 Initialize Bot
bot = Client("mpd_m3u8_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Store Active Downloads
active_downloads = {}

# ✅ START COMMAND
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "**🎥 MPD/M3U8 Downloader Bot**\n\n"
        "🔹 Send me a valid **MPD/M3U8 URL** and I will download & upload it to Telegram.\n"
        "🔹 Supports High-Speed Processing using **TG D4 Cloud**.\n"
        "🔹 Use `/status` to check download progress.\n\n"
        "**⚡ Powered by TG D4 Cloud**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Source Code", url="https://github.com/your_repo")]
        ])
    )

# ✅ STATUS COMMAND
@bot.on_message(filters.command("status"))
async def check_status(client, message):
    if not active_downloads:
        return await message.reply_text("📭 No active downloads at the moment.")

    text = "**🚀 Active Downloads:**\n\n"
    for url, data in active_downloads.items():
        text += f"🔹 **URL:** `{url}`\n"
        text += f"📥 **Progress:** {data['progress']}%\n"
        text += "--------------------\n"

    await message.reply_text(text)

# ✅ CANCEL COMMAND
@bot.on_message(filters.command("cancel"))
async def cancel_download(client, message):
    if not active_downloads:
        return await message.reply_text("⚠️ No active downloads to cancel.")

    for url, data in active_downloads.items():
        task = data['task']
        task.cancel()
        del active_downloads[url]

    await message.reply_text("❌ All active downloads have been cancelled.")

# ✅ HANDLE MPD/M3U8 URL
@bot.on_message(filters.text & filters.private)
async def handle_url(client, message):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")) or not (".mpd" in url or ".m3u8" in url):
        return await message.reply_text("❌ Invalid URL! Please send a **valid MPD or M3U8 link**.")

    await message.reply_text(f"📥 **Processing URL:** `{url}`\nPlease wait...")

    task = asyncio.create_task(download_and_upload(client, message, url))
    active_downloads[url] = {"task": task, "progress": 0}

# ✅ DOWNLOAD & UPLOAD FUNCTION
async def download_and_upload(client, message, url):
    try:
        # 🔹 Downloading File using yt-dlp
        download_path = f"downloads/{message.chat.id}.mp4"
        ydl_opts = {
            'outtmpl': download_path,
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': False,
            'progress_hooks': [lambda d: update_progress(url, d)]
        }

        async with asyncio.Semaphore(2):  # Limit parallel downloads
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        # 🔹 Upload to Telegram using TG D4 Cloud
        await client.send_video(
            chat_id=TARGET_CHANNEL,
            video=download_path,
            caption=f"✅ **Uploaded from URL:** `{url}`",
            progress=upload_progress
        )

        # 🔹 Cleanup
        os.remove(download_path)
        del active_downloads[url]

        await message.reply_text(f"✅ **Successfully Uploaded to {TARGET_CHANNEL}**")

    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")
        if url in active_downloads:
            del active_downloads[url]

# ✅ PROGRESS UPDATE FUNCTION
def update_progress(url, d):
    if d['status'] == 'downloading':
        active_downloads[url]['progress'] = d.get('_percent_str', '0%')

# ✅ UPLOAD PROGRESS BAR
async def upload_progress(current, total):
    progress = (current / total) * 100
    return f"🚀 Uploading... {progress:.2f}%"

# ✅ RUN BOT
print("🚀 Bot is Running...")
bot.run()
