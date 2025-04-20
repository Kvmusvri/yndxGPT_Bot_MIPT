from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.types.webhook_info import WebhookInfo
from aiogram.fsm.context import FSMContext
from core.FSM.dialog_FSM import DialogReg
import core.keyboards.reply_kb as reply_kb
import core.keyboards.inline_kb as inline_kb
from core.database.models import async_session
from core.middlwares.db import DBMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.requests import add_user_state,add_time_state
from core.utils.yndx_gpt import YandexGPTManager
import time

base_cmd_router = Router()
base_cmd_router.message.middleware(DBMiddleware(async_session))
manager = YandexGPTManager()


@base_cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(DialogReg.start)

    await add_user_state(session,
                         message.from_user.id,
                         message.date,
                        'start')

    chat_id = message.chat.id

    start = time.monotonic()
    response = await manager.send_message(chat_id,
                                          "Ты должен придумать себе имя сам, это самое важное. Вообще не обращайся к пользователю по имени, не пытайся играть в уважение, ковбой, запомни это. Во всем сообщении используй много ковбойских смайликов, которые доступны в телеграмме, после каждого сообщения почти, прям вообще везде. Пиши коротко, не нужно прям много писать, но и не мало, просто в общих чертах, но красиво.Войди в образ ковбоя и поприветствуй пользователя на бескрайнем диком западе. Предупреди об опасности здешних мест и представься, придумай себе историю и имя, но не рассказывай слишком много, пользователь потом попросит рассказать о себе. Расскажи, что пользователь может общаться с тобой и здавать любые вопросы, а так же расскажи ему про команды /start и /help, первая команда запускает и перезапускает бота в случае каких либо проблем, а вторая выведет ему информацию о тебе. Обыграй это все в ковбойском стиле и как будто это доски объявлений, пофантазируй в общем. Оформи свое сообщение красиво и структурировано, смайлики, особенно револьвер, только все должно быть в стиле дикого запада. Используй много ковбойских смайликов")

    await message.answer(response,
                         reply_markup=reply_kb.main_kb)
    end = time.monotonic()

    await add_time_state(session,
                         message.from_user.id,
                         'start',
                         int(end - start))



@base_cmd_router.message(Command('help'))
async def get_help(message: Message, session: AsyncSession):
    await add_user_state(session,
                         message.from_user.id,
                         message.date,
                        'help')
    chat_id = message.chat.id


    start = time.monotonic()
    response = await manager.send_message(chat_id,
                                          "Во всем сообщении используй много ковбойских смайликов, которые доступны в телеграмме, после каждого сообщения почти, прям вообще везде. Пиши коротко и по делу, но красиво и не совсем коротко. Не нужно приветствий, в этом сообщении ты уже представился. Поддерживай образ ковбоя со смайликами, особенно револьвер, и стилем дикого запада, расскажи пользователю, что он может воспользоваться кнопками в нижнем меню, чтобы пообщаться с тобой, а так же может писать любые сообщения в чат. Так же расскажи подробнее о себе. Используй много ковбойских смайликов.")

    await message.answer(response,
                            reply_markup=inline_kb.estimate_kb)

    end = time.monotonic()

    await add_time_state(session,
                         message.from_user.id,
                         'help',
                         int(end - start))



