import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Teacher

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/teacher")

@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["teacher"])
async def create_teacher(teacher_name:str, teacher_email:str):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Pydantic Model
                teacher = Teacher(name=teacher_name,email=teacher_email)
                #Create Query
                insert_query = "INSERT INTO teacher (name,email) VALUES (%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (teacher.name,
                                teacher.email,
                                ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return teacher

@router.post("/edit", status_code=status.HTTP_202_ACCEPTED, tags=["teacher"])
async def edit_teacher(teacher_id:int, new_teacher_name:str=None,new_teacher_email:str=None):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Insert into DB
                if new_teacher_name and new_teacher_email:
                    #Create Query
                    update_query = "UPDATE teacher SET name=%s, email=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_teacher_name,
                                    new_teacher_email,
                                    teacher_id,
                                    ))
                elif new_teacher_name:
                    #Create Query
                    update_query = "UPDATE teacher SET name=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_teacher_name,
                                    teacher_id,
                                    ))
                elif new_teacher_email:
                    #Create Query
                    update_query = "UPDATE teacher SET email=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_teacher_email,
                                    teacher_id,
                                    ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return True

@router.post("/delete", status_code=status.HTTP_200_OK, tags=["teacher"])
async def delete_teacher(teacher_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                del_query = "DELETE FROM teacher WHERE id=%s"
                #Delete From DB
                await cur.execute(del_query,
                                (teacher_id,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return True
    
@router.post("/get_teacher_by_id", status_code=status.HTTP_200_OK, tags=["teacher"])
async def get_teacher_by_id(teacher_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM teacher WHERE id=%s"
                #Select From DB
                await cur.execute(sel_query,
                                (teacher_id,))
                results = await cur.fetchall()
                teacher_info = results[0]
                teacher = Teacher(
                            id=teacher_info[0],
                            name = teacher_info[1],
                            email = teacher_info[2])
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return teacher
