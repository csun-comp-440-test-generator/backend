import os
import dotenv

import mysql.connector
from mysql.connector.aio import connect


dotenv.load_dotenv()

async def get_db_session():
        async with await mysql.connector.aio.connect(
            user=os.environ['USER'],
            password=os.environ['PASSWORD'],
            database=os.environ['DATABASE']
        ) as conn:
            yield conn

