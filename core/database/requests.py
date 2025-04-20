from core.database.models import async_session
from sqlalchemy import select, delete, update, func
from sqlalchemy.dialects.postgresql import TEXT
import asyncio
from core.database.models import UserState, TimeState, EstimateState
import json
import pandas as pd
import os

import datetime

async def add_user_state(session, user_tg_id: int, datetime: datetime.datetime, action: str) -> None:
    new_stat = UserState(user_tg_id=user_tg_id, datetime=datetime, action=action)
    session.add(new_stat)
    await session.commit()

async def add_time_state(session, user_tg_id: int,action: str, time_delta: int) -> None:
    new_stat = TimeState(user_tg_id=user_tg_id,  action = action, time_delta=time_delta)
    session.add(new_stat)
    await session.commit()

async def add_est_state(session, user_tg_id: int, est: str) -> None:
    new_stat = EstimateState(user_tg_id=user_tg_id, est=est)
    session.add(new_stat)
    await session.commit()