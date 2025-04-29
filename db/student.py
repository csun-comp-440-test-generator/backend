import sys

# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Student, TestInfoRequest, SectionInfoRequest

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/student")

@router.get("/validate", status_code=status.HTTP_200_OK,)
async def validte_teacher(id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM student WHERE id=%s"
                #Select From DB
                await cur.execute(sel_query,
                                (id,))
                results = await cur.fetchone()
                if results:
                     return True
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return False

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
    
   
@router.get("/get_student_sections", status_code=status.HTTP_200_OK, tags=["section", "student"])
async def get_section_by_student_id(student_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = """
                SELECT
                    s.class_id as class_id,
                    s.id as section_id,
                    c.name as class_name
                FROM class c
                JOIN section s on s.class_id = c.id
                JOIN registered r on r.section_id = s.id
                JOIN student stu on stu.id = r.student_id
                WHERE stu.id = %s
                ORDER BY s.id;"""
                #Select From DB
                await cur.execute(sel_query,
                                (student_id,))
                results = await cur.fetchall()
                sections = []
                for result in results:
                    section_info = result
                    section = SectionInfoRequest(
                        course_id=section_info[0],
                        section_id=section_info[1],
                        course_name=section_info[2],
                    )
                    sections.append(section)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return sections
    
@router.get("/get_registered_exams", status_code=status.HTTP_200_OK, tags=["exam", "student"])
async def get_registered_exams_by_id(student_id:int, section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = """
                SELECT
                    t.id as test_id,
                    t.name as test_name,
                    t.start_time as start_time,
                    t.end_time as end_time
                FROM class c
                JOIN section s on s.class_id = c.id
                JOIN registered r on r.section_id = s.id
                JOIN student stu on stu.id = r.student_id
                JOIN test t on t.section_id = s.id
                WHERE stu.id = %s
                AND s.id = %s
                ORDER BY t.id;"""
                #Select From DB
                await cur.execute(sel_query,
                                (student_id,
                                 section_id))
                results = await cur.fetchall()
                tests = []
                for result in results:
                    test_info = result
                    test = TestInfoRequest(
                        test_id=test_info[0],
                        test_name=test_info[1],
                        start_time=test_info[2],
                        end_time=test_info[3]
                    )
                    tests.append(test)
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return tests
    
@router.get("/get_current_grade", status_code=status.HTTP_200_OK, tags=["exam", "student"])
async def get_current_grade(student_id:int, section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT grade FROM registered WHERE student_id = %s AND section_id = %s;"
                #Select From DB
                await cur.execute(sel_query,
                                (student_id,
                                 section_id))
                results = await cur.fetchone()
                if results[0] != None:
                    grade = results[0]
                    grade = grade*100
                else:
                     grade="NA"
                
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return grade
    


