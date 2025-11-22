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
TOKEN = "8401080682:AAFfFH4ZFOu83rzm98Cu3fauaRkANLVHlXE"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

# Initialize Bot instance with default bot properties which will be passed to all API calls
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def reupdata(key, data):
    await client_redis.set(
        key,
        json.dumps(data, ensure_ascii=False)  # кириллица сохраняется читаемо
    )

# взять с базы что-то
async def redata(key):

    try:
        # data = await json.loads(client_redis.get(key).decode())
        data = await client_redis.get(key)

        data = json.loads(data.decode())
    except Exception as ex:
        # print(f"reupdata - , key {key}", ex)
        data = None
    return data



admin = [310410518]
#####################################################################################
#  Регистрация нового кота

async def post_request_rega(id_telega, data):
    url = "https://worker-production-e29a.up.railway.app/v3"

    try:
        id_telega_int = int(id_telega)
    except ValueError:
        print("Ошибка: id_telega должен быть числом")
        return None

    payload = {
        "method": "start_bot",
        "call_started": "",
        "params": {
            "id_telega": id_telega_int,
            "data": data,
        },
        "qhc": ""
    }

    print("Отправка запроса на:", url)
    print("Данные запроса:", payload)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=False) as response:  # ← ssl=False отключает проверку
                if response.status == 200:
                    data = await response.json()
                    print("Успешный ответ:", data)
                    return data
                else:
                    print(f"Ошибка: HTTP {response.status}")
                    return None
    except Exception as e:
        print("Ошибка при запросе:", e)
        return None


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    Обрабатывает deep links вида: t.me/pokemon_stars_bot/go_stars?startapp=TEST123
    """
    id_telega = message.chat.id
    tt = f"{message.chat.type}"

    if id_telega > 1 and tt == "private":
        pass
    else:
        print("id_telega", id_telega)
        print("message", message)
        return False

    # URL игры
    game_base_url = "https://casinogame-production.up.railway.app/v3"
    startapp_param = None

    # Логируем для отладки
    print(f"📥 Получена команда /start")
    print(f"📝 Текст сообщения: {message.text}")
    print(f"🔗 Полный текст: {message.text}")

    # Способ 1: Проверяем параметр startapp в тексте команды
    # Формат: /start go_stars?startapp=TEST123
    # или: /start?startapp=TEST123
    if message.text:
        # Проверяем формат: /start go_stars?startapp=TEST123
        if '?startapp=' in message.text:
            try:
                # Извлекаем часть после ?startapp=
                parts = message.text.split('?startapp=')
                if len(parts) > 1:
                    # Берем параметр до пробела или конца строки
                    startapp_param = parts[1].split()[0].split('&')[0]
                    print(f"✅ Параметр startapp найден в тексте: {startapp_param}")
            except Exception as e:
                print(f"⚠️ Ошибка при извлечении startapp из текста: {e}")

        # Проверяем формат: /start startapp=TEST123 (без go_stars)
        elif 'startapp=' in message.text:
            try:
                parts = message.text.split('startapp=')
                if len(parts) > 1:
                    startapp_param = parts[1].split()[0].split('&')[0]
                    print(f"✅ Параметр startapp найден (альтернативный формат): {startapp_param}")
            except Exception as e:
                print(f"⚠️ Ошибка при извлечении startapp (альтернативный): {e}")

    # Способ 2: Проверяем entities (для ссылок в сообщении)
    if not startapp_param and message.entities:
        for entity in message.entities:
            if entity.type in ["url", "text_link"]:
                url_text = message.text[entity.offset:entity.offset + entity.length]
                print(f"🔍 Найдена ссылка в entities: {url_text}")
                if '?startapp=' in url_text:
                    try:
                        startapp_param = url_text.split('?startapp=')[1].split('&')[0].split()[0]
                        print(f"✅ Параметр startapp найден в ссылке: {startapp_param}")
                        break
                    except Exception as e:
                        print(f"⚠️ Ошибка при извлечении startapp из ссылки: {e}")

    # Формируем URL игры с параметром
    game_url = game_base_url
    if startapp_param:
        # Добавляем параметр startapp в URL игры
        game_url = f"{game_base_url}?startapp={startapp_param}"
        print(f"🎯 URL игры с параметром: {game_url}")
    else:
        print(f"ℹ️ Параметр startapp не найден, используем базовый URL: {game_url}")

    # Получаем данные пользователя
    user_n = message.chat.username
    first_n = message.from_user.first_name
    last_n = message.from_user.last_name
    language = message.from_user.language_code

    # Извлекаем реферальный код из старого формата (если есть)
    ref_code = message.text[7:] if len(message.text) > 7 else ""

    # Убираем startapp из ref_code, если он там есть
    if ref_code and '?startapp=' in ref_code:
        ref_code = ref_code.split('?startapp=')[0]


    data = {
        "id": id_telega,
        "username": user_n,
        "first_name": first_n,
        'last_name': last_n,
        'language_code': language
    }

    # Текст сообщения
    if language == "ru":
        mess = "Кидай <b>Покеболы</b> и умножай свои Starts"
        mess_botton = "Забрать 100 Здвезд"

    else:
        mess = "Кидай <b>Покеболы</b> и умножай свои Starts"
        mess_botton = "Забрать 100 Здвезд"

    # Создаем кнопку с Mini App
    # Если есть startapp_param, передаем его через start_parameter (для Telegram API)
    # И также добавляем в URL (для фронтенда)


    web_app_info = WebAppInfo(url=game_url)
    if startapp_param:
        # Передаем параметр через start_parameter для Telegram API
        web_app_info = WebAppInfo(
            url=game_url,
            start_parameter=startapp_param
        )
        print(f"📤 Передаем startapp через start_parameter: {startapp_param}")

    bt_by_viki = InlineKeyboardButton(
        text=mess_botton,
        web_app=web_app_info
    )

    # Создание клавиатуры
    kb = InlineKeyboardMarkup(inline_keyboard=[[bt_by_viki]])

    mm = await bot.send_message(
        id_telega,
        mess,
        reply_markup=kb,
        message_effect_id="5046509860389126442"
    )

    # Регаем человека (раскомментируйте если нужно)
    await post_request_rega(id_telega, data)

    # Пытаемся закрепить сообщение
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=mm.message_id)
    except Exception as e:
        print(f"⚠️ Не удалось закрепить сообщение: {e}")





# Обработчик для всех сообщений в супергруппе
# @dp.message()
# async def chek_m(message: types.Message):
#
#
#     # Проверяем, что сообщение пришло из супергруппы
#     # if message.chat.type == "supergroup":
#     #     user_id = message.from_user.id  # Получаем ID пользователя
#     #     chat_id = message.chat.id  # Получаем ID супергруппы
#     #
#     #     # print(message)
#     #
#     #     # print(f"Сообщение из супергруппы {chat_id}, от пользователя {user_id}. Текст: {message.text}")
#     #     try:
#     #         # Получаем текущее время в формате секунд с начала эпохи
#     #         tim0 = time.time()
#     #
#     #         # сегодня дата
#     #         day = time.strftime("%Y-%m-%d", time.localtime(tim0))
#     #
#     #         # данные игрока
#     #         user_caht = await redata(f"chat:{user_id}")
#     #
#     #         if user_caht != None:
#     #
#     #             # манипулии с данными
#     #
#     #             # проверсяем если все хорошо
#     #             if (tim0 - user_caht["old_time"]) < (24 * 60 * 60):
#     #
#     #                 # последний день юзера
#     #                 old_day_user = time.strftime("%Y-%m-%d", time.localtime(user_caht["old_time"]))
#     #                 if old_day_user != day:
#     #                     user_caht["old_day"] = day
#     #                     user_caht["value_day"] += 1
#     #
#     #                 user_caht["old_time"] = tim0
#     #                 user_caht["value_mess"] += 1
#     #
#     #             else:
#     #
#     #                 user_caht["old_time"] = tim0
#     #                 user_caht["old_day"] = day
#     #                 user_caht["old_time"] = 0
#     #                 user_caht["value_mess"] = 0
#     #
#     #
#     #
#     #             await reupdata(f"chat:{user_id}", user_caht)
#     #
#     #
#     #
#     #
#     #         else:
#     #
#     #             # Создаем данные для игрока
#     #             dd = {
#     #                 "id_telega": user_id,
#     #                 "old_time": tim0,
#     #                 "old_day": time.strftime("%Y-%m-%d", time.localtime(time.time())),
#     #                 "value_mess": 1,
#     #                 "value_day": 0,
#     #                 "day_gift": 0
#     #             }
#     #
#     #             await reupdata(f"chat:{user_id}", dd)
#     #
#     #     except Exception as ex:
#     #
#     #         mess = f"Ошибка в чекере времея в чате: {ex},\nuser_id: {user_id}"
#     #         print(mess)
#     #         await bot.send_message(310410518, mess)
#     #
#     #
#     #
#     if message.chat.type == "private":
#         print(message)
#
#         user_id = message.from_user.id  # Получаем ID пользователя
#         chat_id = message.chat.id
#
#
#         # if user_id == 310410518:
#         #     urll = "https://t.me/mastercatonlinebot/mastercats"
#         #     mess = f"Master Cat Online"
#         #
#         #     # Создание кнопки с веб-приложением
#         #     bt_by_viki = InlineKeyboardButton(text="Play Master Cat", url=urll)
#         #
#         #     # Создание клавиатуры с использованием inline_keyboard
#         #     kb = InlineKeyboardMarkup(inline_keyboard=[[bt_by_viki]])
#         #
#         #     await bot.send_message(int(-1002301080691), mess, reply_markup=kb)
#         #
#         # # -1002301080691



###### Саша

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """
    Этот хэндлер вызывается, когда пользователь переходит к оплате,
    и Telegram просит у нас подтверждения, можно ли продолжать.
    """

    await pre_checkout_query.answer(ok=True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """
    Обработка успешного платежа.
    Здесь мы вызываем refund в Stars через метод `refund_star_payment`.
    """
    payment_info = message.successful_payment

    provider_payment_charge_id = payment_info.telegram_payment_charge_id

    # try:
    #     result = await bot.refund_star_payment( user_id=message.from_user.id, telegram_payment_charge_id=provider_payment_charge_id)
    # except Exception as e:
    #     await message.answer(f"Ошибка при возврате платежа: <b>{str(e)}</b>")


@dp.message(Command("paysupport"))
async def cmd_pay_support(message: Message):

    # тут надо текст нашего сапорта котрый ответит в случае если чето вопросы есть

    support_text = (
        "Support\n\n"
        "If you have problems with payments, please contact our support team.\n\n"
        "Feedback bot: @komarovskij91"
    )

    await message.answer(support_text)




async def main() -> None:


    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())