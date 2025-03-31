import os
import dotenv

from fastapi import APIRouter, status

import mysql.connector
from mysql.connector.aio import connect
from pydantic import BaseModel

class Student(BaseModel):
    id: int
    name: str
    email: str


router = APIRouter(prefix="/db")

dotenv.load_dotenv()

async def get_db_session():
        async with await mysql.connector.aio.connect(
            user=os.environ['USER'],
            password=os.environ['PASSWORD'],
            database=os.environ['DATABASE']
        ) as conn:
            yield conn

@router.get("/student", status_code=status.HTTP_200_OK)
async def get_students():
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            await cur.execute("SELECT * FROM student")
            results = await cur.fetchall()
            student_info = results[0]
            student = Student(
                 id = student_info[0],
                 name=student_info[1],
                 email=student_info[2]
            )
            return student
