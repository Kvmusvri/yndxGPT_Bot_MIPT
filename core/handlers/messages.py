import asyncio
import time
from core.FSM.dialog_FSM import DialogReg
from aiogram import F, Router
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from core.database.models import async_session
from core.middlwares.db import DBMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import re
from core.utils.yndx_gpt import YandexGPTManager
import core.keyboards.inline_kb as inline_kb
from core.database.requests import add_user_state, add_time_state
import time


dialog_router = Router()
dialog_router.message.middleware(DBMiddleware(async_session))
manager = YandexGPTManager()



@dialog_router.message()
async def handle_message(message: Message, session: AsyncSession):
    await add_user_state(session,
                         message.from_user.id,
                         message.date,
                         message.text)

    chat_id = message.chat.id

    start = time.monotonic()
    response = await manager.send_message(chat_id, message.text)

    await message.answer(response,
                         reply_markup=inline_kb.estimate_kb)
    end = time.monotonic()

    await add_time_state(session,
                         message.from_user.id,
                         message.text,
                         int(end - start))
