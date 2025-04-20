import sys

from pydantic import BaseModel
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Course

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/course")

@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["course"])
async def create_course(course_id:int, course_name:str):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Pydantic Model
                course = Course(id=course_id,name=course_name)
                #Create Query
                insert_query = "INSERT INTO class (id,name) VALUES (%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (course.id,
                                course.name,
                                ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return course

@router.post("/edit", status_code=status.HTTP_202_ACCEPTED, tags=["course"])
async def edit_course(course_id:int, new_course_id:int=None,new_course_name:str=None):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Insert into DB
                if new_course_id and new_course_name:
                    #Create Query
                    update_query = "UPDATE class SET id=%s, name=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_course_id,
                                    new_course_name,
                                    course_id,
                                    ))
                elif new_course_id:
                    #Create Query
                    update_query = "UPDATE class SET id=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_course_id,
                                    course_id,
                                    ))
                elif new_course_name:
                    #Create Query
                    update_query = "UPDATE class SET name=%s WHERE id = %s"
                    await cur.execute(update_query,
                                    (new_course_name,
                                    course_id,
                                    ))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return True

@router.delete("/delete", status_code=status.HTTP_200_OK, tags=["course"])
async def delete_course(course_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                del_query = "DELETE FROM class WHERE id=%s"
                #Delete From DB
                await cur.execute(del_query,
                                (course_id,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return True
    
@router.get("/get_course_by_id", status_code=status.HTTP_200_OK, tags=["course"])
async def get_course_by_id(course_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM class WHERE id=%s"
                #Select From DB
                await cur.execute(sel_query,
                                (course_id,))
                results = await cur.fetchall()
                course_info = results[0]
                course = Course(
                            id = course_info[0],
                            name = course_info[1])
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return course
    
@router.get("/get_courses", status_code=status.HTTP_200_OK, tags=["course"])
async def get_all_courses():
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM class"
                #Select From DB
                await cur.execute(sel_query,)
                results = await cur.fetchall()
                courses = []
                for res in results:
                    course_info = res
                    course = Course(
                                id = course_info[0],
                                name = course_info[1])
                    courses.append(course)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return courses
    


