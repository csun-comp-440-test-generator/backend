import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Assistant, SectionInfoRequest

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/assistant", tags=["teaching assistant"])

@router.get("/validate", status_code=status.HTTP_200_OK,)
async def validte_teacher(id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM teaching_assistant WHERE id=%s"
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
    
@router.post("/get_by_id", status_code=status.HTTP_200_OK)
async def get_by_id(assistant_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Query
                sel_query = "SELECT * FROM teaching_assistant WHERE id=%s"
                #Select From DB
                await cur.execute(sel_query,
                                (assistant_id,))
                results = await cur.fetchall()
                assistant_info = results[0]
                assistant = Assistant(
                            id=assistant_info[0],
                            name = assistant_info[1],
                            email = assistant_info[2])
    except Error as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return assistant
    
@router.get("/get_sections", status_code=status.HTTP_200_OK, tags=["section"])
async def get_sections_by_id(assistant_id:int):
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
                JOIN teaching_assistant a on a.id = s.teaching_assistant
                WHERE a.id = %s
                ORDER BY s.id;"""
                #Select From DB
                await cur.execute(sel_query,
                                (assistant_id,))
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