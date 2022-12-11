from aiogram import Bot, Dispatcher, executor,types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pytube import YouTube

import config
import sqlite3
import logging

connect = sqlite3.connect('users.db')
cur  = connect.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    username VARCHAR(255),
    id INTEGER,
    chat_id INTEGER
    );
    """)
connect.commit()

bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

class DownloadAudio(StatesGroup):
    download = State()

class DownloadVideo(StatesGroup):
    download = State()

class InfoVideo(StatesGroup):
    info = State()

def infod(url):
    yt_info = YouTube(url)
    yt_info.description
        


def download(url,type):
    yt = YouTube(url)
    if type == "audio":
        yt.streams.filter(only_audio=True).first().download("audio",f"{yt.title}.mp3")
        return f"{yt.title}.mp3"

    elif type =="video":
        yt.streams.filter(progressive=True, file_extension = "mp4").first().download("video", f"{yt.title}.mp4")
        return f"{yt.title}.mp4"

@dp.message_handler(commands=["start"])
async def start(message : types.Message):
    cur  = connect.cursor()
    cur.execute(f"SELECT id FROM users WHERE  id  == {message.from_user.id};")
    result = cur.fetchall()
    if result ==[]:
        cur.execute(f"INSERT INTO users VALUES ('{message.from_user.username}', {message.from_user.id}, {message.chat.id});")
    connect.commit()
    await message.answer(f"Здравстуйте,{message.from_user.full_name} .Меня зовут Tolobrun.\nЕсли хотите узнать обо мне больше нажмите: /help ")

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer("Привет Я черный! \nВот мои команды:\n/start - Запустить бота\n/help - Помощь\n/mailing - Сделать рассылку.\n/video_info - Узнать информацию о видео.\n/video_download - Скачать видео из Ютуб.\n/audio_download - Скачать аудио из Ютуб")

class MailingState(StatesGroup):
    mailing = State()


@dp.message_handler(commands=["mailing"])
async def mailing(message : types.Message):
    await message.answer('Введите сообщение рассылки: ')
    await MailingState.mailing.set()
    


@dp.message_handler(state=MailingState.mailing)
async def mailing(message : types.Message, state : FSMContext):

    try:
        await message.answer("Началась рассылка")
        
        cur.execute("SELECT chat_id FROM users;")
        result = cur.fetchall()
        for i in result:

            await bot.send_message(chat_id=int(i[0]), text = message.text)
        await state.finish()
    except:
        await message.answer("Произошла ошибка, повторите попытку позже")
        await state.finish()

@dp.message_handler(commands=["video_download"])
async def video_download(message: types.Message):
    await message.answer("Отправьте ссылку на видео в ютубе и я вам его отправлю")
    await DownloadVideo.download.set()

@dp.message_handler(state=DownloadVideo.download)
async def download_video(message: types.Message, state : FSMContext):
    try:
        title = download(message.text, "video")
        video = open(f"video/{title}", "rb")
        await message.answer("Скачиваем видео файл ожидайте...")
        try:
            await message.answer("Все скачалось вот держи")
            await bot.send_video(message.chat.id, video)
        except:
            await message.answer("Произошла ошибка, попробуйте позже")
        await state.finish()
    except:
        await message.answer("Неверная ссылка на видео")
        await state.finish()

@dp.message_handler(commands="audio_download")
async def audio_download(message: types.Message):
    await message.answer("Отправьте ссылку на видео и я вам отправлю его в mp3")
    await DownloadAudio.download.set()

@dp.message_handler(state=DownloadAudio.download)
async def download_audio(message: types.Message, state : FSMContext):
    try:
        title = download(message.text, "audio")
        audio = open(f"audio/{title}", "rb")
        await message.answer("Скачиваем файл ожидайте...")
        try:
            await message.answer("Все скачалось вот держи")
            await bot.send_audio(message.chat.id, audio)
        except:
            await message.answer("Произошла ошибка, попробуйте позже")
        await state.finish()
    except:
        await message.answer("Неверная ссылка на видео")
        await state.finish()

@dp.message_handler(commands=["video_info"])
async def video_download(message: types.Message):
    await message.answer("Отправьте ссылку на видео в ютубе и я дам вам о нем информацию")
    await InfoVideo.info.set()

@dp.message_handler(state=InfoVideo.info)
async def info(message: types.Message,state :FSMContext,):
        yt_infoa = infod()
        await message.answer(f"desc: {yt_infoa.description}")
    

executor.start_polling(dp)