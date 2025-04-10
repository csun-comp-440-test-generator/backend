import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Section
from db.models import Student
from pydantic import BaseModel
from typing import Optional

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

class CreateSectionReqeust(BaseModel):
    course_id: int
    teacher_id: int
    assistant_id: Optional[int] = None

router = APIRouter(prefix="/section")

@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["section"])
async def create_section(section_data: CreateSectionReqeust):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                if section_data.assistant_id is not None:
                    #Create Query
                    insert_query = "INSERT INTO section (class_id,teacher,teaching_assistant) VALUES (%s,%s,%s)"
                    #Insert into DB
                    await cur.execute(insert_query,
                                    (
                                    section_data.course_id,
                                    section_data.teacher_id,
                                    section_data.assistant_id,
                                    ))
                else:
                    insert_query = "INSERT INTO section (class_id,teacher) VALUES (%s,%s)"
                    #Insert into DB
                    await cur.execute(insert_query,
                                    (
                                    section_data.course_id,
                                    section_data.teacher_id,
                                    ))                     
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return section_data

@router.post("/edit", status_code=status.HTTP_202_ACCEPTED, tags=["section"])
async def edit_section(section_id:int,new_section_teacher:int=None,new_section_assistant:int=None):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                updates = []
                values = []
                
                if new_section_teacher is not None:
                    updates.append("teacher=%s")
                    values.append(new_section_teacher)

                if new_section_assistant is not None:
                    updates.append("teaching_assistant=%s")
                    values.append(new_section_assistant)   
    
                query=f"UPDATE section SET {','.join(updates)} WHERE id=%s"
                values.append(section_id)
                await cur.execute(
                     query,tuple(values)
                )
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return True

@router.post("/delete", status_code=status.HTTP_200_OK, tags=["section"])
async def delete_section(section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                del_query = "DELETE FROM section WHERE id=%s"
                #Delete From DB
                await cur.execute(del_query,
                                (section_id,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return True
    
@router.get("/get_section_info", status_code=status.HTTP_200_OK, tags=["section"])
async def get_section_by_id(section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = """
                SELECT
                    s.class_id as class_id,
                    s.id as section_id,
                    t.id as teacher_id,
                    t.name as teacher,
                    c.name as class_name
                FROM section s
                JOIN class c on c.id = s.class_id
                JOIN teacher t on t.id = s.teacher
                WHERE s.id = %s;"""
                #Select From DB
                await cur.execute(sel_query,
                                (section_id,))
                results = await cur.fetchall()
                section_info = results[0]
                section = Section(
                            course = section_info[0],
                            id= section_info[1],
                            teacher = section_info[2],
                            teacher_name=section_info[3],
                            course_name=section_info[4],
                            #assistant = section_info[4],
                            #assistant_name=section_info[5]
                            )
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return section

@router.get("/get_registered_students", status_code=status.HTTP_200_OK, tags=["section"])
async def get_students_by_section_id(section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = """
                SELECT
                    s.class_id as class_id,
                    s.id as section_id,
                    c.name as class_name,
                    stu.id as student_id,
                    stu.name as student_name,
                    stu.email as student_email
                FROM class c
                JOIN section s on s.class_id = c.id
                JOIN registered r on r.section_id = s.id
                JOIN student stu on stu.id = r.student_id;
                WHERE section_id=%s"""
                #Select From DB
                await cur.execute(sel_query,
                                (section_id,))
                results = await cur.fetchall()
                registered = {                        
                            "class_id":results[0][0],
                            "section_id":results[0][1],
                            "class_name":results[0][2],
                            "students":[]
                            }
                students=[]
                for i in range(len(results)):
                    registration_info = results[0]
                    student = Student(
                        id=registration_info[3],
                        name=registration_info[4],
                        email=registration_info[5])
                    students.append(student)
                registered["students"] = students
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return registered