import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

# Bot tokeningiz
API_TOKEN = '8508472995:AAGO683iLtW5cifOXar8xx9hcn-jCVwoTZM'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Matnlar va tillar
texts = {
    'uz': {
        'ask_link': "Iltimos, menga Instagram havolasini yuboring. Men sizga videoni taqdim etaman. ✨",
        'error': "Kechirasiz, siz bergan link xato! ❌",
        'wait': "Iltimos, kuting... 🔄",
        'music_btn': "🎵 Video musiqasi"
    },
    'ru': {
        'ask_link': "Пожалуйста, отправьте мне ссылку на Instagram. Я пришлю вам видео. ✨",
        'error': "Извините, предоставленная вами ссылка неверна! ❌",
        'wait': "Пожалуйста, подождите... 🔄",
        'music_btn': "🎵 Музыка из видео"
    },
    'en': {
        'ask_link': "Please send me an Instagram link. I will provide the video for you. ✨",
        'error': "Sorry, the link you provided is incorrect! ❌",
        'wait': "Please wait... 🔄",
        'music_btn': "🎵 Video music"
    }
}

user_lang = {}

def get_lang_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data='lang_uz'),
        InlineKeyboardButton("🇷🇺 Русский язык", callback_data='lang_ru'),
        InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "Assalomu alaykum! 👋\n\n"
        "Ushbu bot orqali Instagram videolarini va ularning musiqalarini yuklab olishingiz mumkin. 📥\n\n"
        "Iltimos, tilni tanlang: 👇"
    )
    await message.answer(welcome_text, reply_markup=get_lang_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    user_lang[callback_query.from_user.id] = lang
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, texts[lang]['ask_link'])

@dp.message_handler()
async def handle_video(message: types.Message):
    lang = user_lang.get(message.from_user.id, 'uz')
    url = message.text

    if "instagram.com" not in url:
        await message.reply(texts[lang]['error'])
        return

    wait_msg = await message.answer(texts[lang]['wait'])

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            keyboard = InlineKeyboardMarkup()
            music_btn = InlineKeyboardButton(texts[lang]['music_btn'], callback_data=f"music_{url}")
            keyboard.add(music_btn)

            await bot.send_video(message.chat.id, video_url, reply_markup=keyboard)
            await wait_msg.delete()
    except Exception:
        await wait_msg.edit_text(texts[lang]['error'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
