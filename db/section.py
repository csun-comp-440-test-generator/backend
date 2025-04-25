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

class EnrollSectionRequest(BaseModel):
    student_id:int
    section_id:int

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
    
@router.get("/get_all_section_info", status_code=status.HTTP_200_OK, tags=["section"])
async def get_sections():
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
                JOIN teacher t on t.id = s.teacher;"""
                #Select From DB
                await cur.execute(sel_query,)
                results = await cur.fetchall()
                sections=[]
                for section_info in results:
                    section = Section(
                                course = section_info[0],
                                id= section_info[1],
                                teacher = section_info[2],
                                teacher_name=section_info[3],
                                course_name=section_info[4],
                                #assistant = section_info[4],
                                #assistant_name=section_info[5]
                                )
                    sections.append(section)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return sections
    
@router.get("/get_unregistered_section_info", status_code=status.HTTP_200_OK, tags=["section"])
async def get_unregistered_sections(student_id:int):
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
                LEFT JOIN registered r on r.section_id = s.id
                AND r.student_id = %s
                WHERE r.section_id IS NULL;"""
                #Select From DB
                await cur.execute(sel_query,
                                (student_id,))
                results = await cur.fetchall()
                sections=[]
                for section_info in results:
                    section = Section(
                                course = section_info[0],
                                id= section_info[1],
                                teacher = section_info[2],
                                teacher_name=section_info[3],
                                course_name=section_info[4],
                                #assistant = section_info[4],
                                #assistant_name=section_info[5]
                                )
                    sections.append(section)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return sections
    
@router.post("/enroll", status_code=status.HTTP_201_CREATED, tags=["section"])
async def enroll_student(enroll_data: EnrollSectionRequest):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                insert_query = "INSERT INTO registered (student_id,section_id) VALUES (%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (
                                enroll_data.student_id,
                                enroll_data.section_id,
                                ))                     
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return enroll_data
    
@router.post("/update_grade", status_code=status.HTTP_200_OK, tags=["section"])
async def update_student_grade(student_id,section_id):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                sel_query = """
                    SELECT
                        sub.test_id as test_id,
                        sub.score as grade,
                        c.id as class_id,
                        s.id as section_id,
                        c.name as class_name,
                        t.name as test_name,
                        t.id as test_id
                    FROM test_submission sub
                    JOIN test t ON t.id=sub.test_id
                    JOIN section s ON s.id = t.section_id
                    JOIN class c ON c.id=s.class_id
                    WHERE s.id = %s AND sub.student_id = %s;
                    """
                #Insert into DB
                await cur.execute(sel_query,
                                (section_id,
                                student_id,
                                ))  
                results = await cur.fetchall()
                total_grade = 0
                for entry in results:
                     total_grade += float(entry[1])
                
                if len(results) > 0:
                    total_grade /= len(results)

                insert_query = "UPDATE registered SET grade=%s WHERE student_id = %s AND section_id = %s"
                #Insert into DB
                await cur.execute(insert_query,
                                (total_grade,
                                student_id,
                                section_id,
                                ))    
                     
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return total_grade
    
class OpenSection(BaseModel):
     course_id:int
     section_id:int
     course_name:str
    
@router.get("/get_open_sections", status_code=status.HTTP_200_OK, tags=["section", "teaching assistant"])
async def get_open_sections(assistant_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = """
                SELECT
                    s.class_id as class_id,
                    s.id as section_id,
                    c.name as class_name
                FROM section s
                JOIN class c on c.id = s.class_id
                LEFT JOIN teaching_assistant a on a.id = s.teaching_assistant
                AND a.id = %s
                WHERE a.id IS NULL"""
                #Select From DB
                await cur.execute(sel_query,
                                (assistant_id,))
                results = await cur.fetchall()
                sections=[]
                for section_info in results:
                    section = OpenSection(
                                course_id = section_info[0],
                                section_id = section_info[1],
                                course_name = section_info[2],)
                    sections.append(section)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return sections
    
class RegisterAssistantSection(BaseModel):
     section_id:int
     assistant_id:int
    
@router.post("/register_assistant", status_code=status.HTTP_201_CREATED, tags=["section"])
async def register_assistant(register_data: RegisterAssistantSection):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                update_query = "UPDATE section SET teaching_assistant = %s WHERE id=%s"
                #Update DB
                await cur.execute(update_query,
                                (register_data.assistant_id,
                                register_data.section_id,
                                ))                     
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return register_data