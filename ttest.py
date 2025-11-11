import asyncio
import logging
import sys
from os import getenv

import aiohttp

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, FSInputFile, PreCheckoutQuery, ContentType
from aiogram.types.input_file import InputFile
import json

import time
import motor.motor_asyncio
import random
import requests

import redis.asyncio as aioredis

from aiogram import F
import os


redis_url = os.getenv("REDIS_URL")
if not redis_url:
    # Строка подключения
    redis_url = "redis://default:PoMGWkghyNOhahqsulDlTzFfzNUixrWL@maglev.proxy.rlwy.net:30329"
    print("конект через публик")
else:
    print("Коннект через приватку к редис")

# Создаем объект Redis
client_redis = aioredis.from_url(redis_url)





# Bot token can be obtained via https://t.me/BotFather
TOKEN = "8036216160:AAHwGBXCA-SWBGP6GqC8dd4uJX1q-RnR0NE"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

# Initialize Bot instance with default bot properties which will be passed to all API calls
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# CHANNEL_ID = -1002450731122
# chat = -1002301080691







async def ttt():

    mess = "Круто играешь! Подписывайся на наши социальные сети, чтобы быть в курсе всех обновлений и розыгрышей игры!" \
           "\n\nTwitter (X) — https://x.com/giftsbeats" \
           "\nTelegram ENG — https://t.me/GiftsBeats" \
           "\nTelegram RU — https://t.me/GiftsBeats_ru"

    await asyncio.sleep(2)

    await bot.send_message(310410518, mess, disable_web_page_preview=True)



asyncio.get_event_loop().run_until_complete(ttt())