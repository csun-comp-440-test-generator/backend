import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
from db.client import get_db_session

from fastapi import APIRouter, status
from pydantic import BaseModel

class Student(BaseModel):
    id: int
    name: str
    email: str

dotenv.load_dotenv()

router = APIRouter(prefix="/db")

@router.get("/student", status_code=status.HTTP_200_OK)
async def get_students():
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM student"
            await cur.execute(select_query)
            results = await cur.fetchall()
            student_info = results[0]
            student = Student(
                 id = student_info[0],
                 name=student_info[1],
                 email=student_info[2]
            )
            return student
