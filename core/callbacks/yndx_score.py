import core.keyboards.reply_kb as reply_kb
from core.FSM.dialog_FSM import DialogReg
from aiogram.fsm.context import FSMContext
import core.keyboards.inline_kb as inline_kb
from core.middlwares.db import DBMiddleware

from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import async_session
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
import re
import os
import json
import ast
from dotenv import load_dotenv, set_key, get_key, dotenv_values
import dotenv
from aiogram.types import InputMediaPhoto, InputMediaVideo
import asyncio
from core.database.requests import add_est_state, add_user_state, add_time_state
from core.utils.yndx_gpt import YandexGPTManager
import time



clbs_router = Router()
clbs_router.callback_query.middleware(DBMiddleware(async_session))
manager = YandexGPTManager()



@clbs_router.callback_query(F.data=="est_good")
async def callback_est_good(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    await add_user_state(session,
                         callback_query.from_user.id,
                         callback_query.message.date,
                         'estimate')

    await add_est_state(session,
                        callback_query.from_user.id,
                        'good'
                        )

    chat_id = callback_query.message.chat.id

    start = time.monotonic()

    response = await manager.send_message(chat_id,
                                          "Пиши коротко, это должно быть радостное сообщение. Продолжай образ ковбоя и поблагодари пользователя за хороший отзыв")
    await callback_query.message.answer(callback_query.message.text)
    await callback_query.message.delete()

    await callback_query.message.answer(response,
                         reply_markup=reply_kb.main_kb)

    end = time.monotonic()

    await add_time_state(session,
                         callback_query.from_user.id,
                         'estimate',
                         int(end - start))



@clbs_router.callback_query(F.data=="est_bad")
async def callback_est_good(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    await add_user_state(session,
                         callback_query.from_user.id,
                         callback_query.message.date,
                         'estimate')


    await add_est_state(session,
                        callback_query.from_user.id,
                        'bad'
                        )

    chat_id = callback_query.message.chat.id

    start = time.monotonic()

    response = await manager.send_message(chat_id,
                                          "Пиши коротко, это должно быть сообщение обиды и злобы. Продолжай образ ковбоя и искренне разочаруйся в пользователе за плохой отзыв. Скажи, что раз ему так не нравится, то может ему и не стоило появлятся на диком западе, сделай вид, что достаешь пистолет и пригрози пользователю, а дальше скажи ему выметаться. Обыграй это все в агрессивной игровой форме ковбоя.")

    await callback_query.message.answer(callback_query.message.text)
    await callback_query.message.delete()

    await callback_query.message.answer(response,
                                        reply_markup=reply_kb.main_kb)

    end = time.monotonic()

    await add_time_state(session,
                         callback_query.from_user.id,
                         'estimate',
                         int(end - start))