import os
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import UserState, TimeState, EstimateState  # Импортируем таблицы из модели
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


load_dotenv()

engine = create_async_engine(url=os.getenv('DATABASE_URL'))

async_session = async_sessionmaker(engine)

# Функция для удаления часового пояса из datetime
def convert_datetime_timezone_aware_to_naive(df: pd.DataFrame) -> pd.DataFrame:
    # Преобразуем все столбцы с типом datetime в datetime без часового пояса
    for column in df.select_dtypes(include=['datetime64[ns, UTC]']):
        df[column] = df[column].dt.tz_localize(None)  # Удаляем информацию о часовом поясе
    return df

# Функция для преобразования объектов SQLAlchemy в словарь, исключая _sa_instance_state
def object_to_dict(obj):
    # Берем все атрибуты объекта, исключая _sa_instance_state
    data = {key: value for key, value in vars(obj).items() if key != '_sa_instance_state'}
    return data

# Функция экспорта в Excel
async def export_to_xlsx():
    async with async_session() as session:
        # Получаем все записи из таблиц
        result_user_stats = await session.execute(select(UserState))
        result_time_stats = await session.execute(select(TimeState))
        result_est_stats = await session.execute(select(EstimateState))

        # Преобразуем результат в pandas DataFrame, исключая _sa_instance_state
        user_stats_data = [object_to_dict(row) for row in result_user_stats.scalars()]
        time_stats_data = [object_to_dict(row) for row in result_time_stats.scalars()]
        est_stats_data = [object_to_dict(row) for row in result_est_stats.scalars()]

        # Преобразуем в DataFrame
        user_stats_df = pd.DataFrame(user_stats_data)
        time_stats_df = pd.DataFrame(time_stats_data)
        est_stats_df = pd.DataFrame(est_stats_data)

        # Преобразуем все datetime с часовым поясом в без часового пояса
        user_stats_df = convert_datetime_timezone_aware_to_naive(user_stats_df)
        time_stats_df = convert_datetime_timezone_aware_to_naive(time_stats_df)
        est_stats_df = convert_datetime_timezone_aware_to_naive(est_stats_df)

        # Создаем папки для каждой таблицы, если их нет
        os.makedirs('exports/user_stats', exist_ok=True)
        os.makedirs('exports/time_stats', exist_ok=True)
        os.makedirs('exports/est_stats', exist_ok=True)

        # Экспортируем в Excel
        user_stats_df.to_excel('exports/user_stats/user_stats.xlsx', index=False, engine='openpyxl')
        time_stats_df.to_excel('exports/time_stats/time_stats.xlsx', index=False, engine='openpyxl')
        est_stats_df.to_excel('exports/est_stats/est_stats.xlsx', index=False, engine='openpyxl')

        print("Экспорт завершен!")

# Основная асинхронная функция для запуска
async def main():
    # Выполнение экспорта
    await export_to_xlsx()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
