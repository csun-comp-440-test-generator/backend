import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Student

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/student")

@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["student"])
async def create_student(student_name:str, student_email:str):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Pydantic Model
                student = Student(name=student_name,email=student_email)
                #Create Query
                insert_query = "INSERT INTO student (name,email) VALUES (%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (student.name,
                                student.email,
                                ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return student

@router.post("/edit", status_code=status.HTTP_202_ACCEPTED, tags=["student"])
async def edit_student(student_id:int, new_student_name:str=None,new_student_email:str=None):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Insert into DB
                if new_student_name and new_student_email:
                    #Create Query
                    update_query = "UPDATE student SET name=%s, email=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_student_name,
                                    new_student_email,
                                    student_id,
                                    ))
                elif new_student_name:
                    #Create Query
                    update_query = "UPDATE student SET name=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_student_name,
                                    student_id,
                                    ))
                elif new_student_email:
                    #Create Query
                    update_query = "UPDATE student SET email=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_student_email,
                                    student_id,
                                    ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return True

@router.post("/delete", status_code=status.HTTP_200_OK, tags=["student"])
async def delete_student(student_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                del_query = "DELETE FROM student WHERE id=%s"
                #Delete From DB
                await cur.execute(del_query,
                                (student_id,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return True
    
@router.post("/get_student_by_id", status_code=status.HTTP_200_OK, tags=["student"])
async def get_student_by_id(student_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM student WHERE id=%s"
                #Select From DB
                await cur.execute(sel_query,
                                (student_id,))
                results = await cur.fetchall()
                student_info = results[0]
                student = Student(
                            id=student_info[0],
                            name = student_info[1],
                            email = student_info[2])
    except Error as err:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,detail=f"Error: {err}")
    else:
        return student
    
@router.post("/register_section", status_code=status.HTTP_201_CREATED, tags=["student"])
async def register_student_to_section(student_id:int,section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                insert_query = "INSERT INTO registered (student_id,section_id) VALUES (%s,%s)"
                #Select From DB
                await cur.execute(insert_query,
                                (student_id,
                                 section_id))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,detail=f"Error: {err}")
    else:
        return True
    


