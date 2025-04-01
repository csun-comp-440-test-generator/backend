import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime

from db.client import get_db_session

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional

class Test(BaseModel):
    id: Optional[int] = None
    section_id: int
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None

dotenv.load_dotenv()

router = APIRouter(prefix="/test")

@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["exam"])
async def create_test(section_id:int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            #Create Pydantic Model
            test = Test(section_id=section_id)
            #Create Query
            insert_query = "INSERT INTO test (section_id) VALUES (%s)"
            #Insert into DB
            await cur.execute(insert_query,
                              (test.section_id,)
                              )
        await conn.commit()
        return test
        
@router.get("/retrieve_by_section_id", status_code=status.HTTP_200_OK, tags=["exam"])
async def get_tests_by_section_id(section_id: int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM test WHERE section_id = %s"
            await cur.execute(
                select_query,
                (section_id,)
                )
            results = await cur.fetchall()
            tests=[]
            for i in range(len(results)):
                test_info = results[i]
                test = Test(
                    id = test_info[0],
                    section_id = test_info[1],
                    start_time=test_info[2],
                    end_time=test_info[3]
                )
                tests.append(test)
            return tests
        
@router.get("/retrieve_by_test_id", status_code=status.HTTP_200_OK, tags=["exam"])
async def get_tests_by_section_id(test_id: int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM test WHERE id = %s"
            await cur.execute(
                select_query,
                (test_id,)
                )
            results = await cur.fetchall()
            test_info = results[0]
            test = Test(
                id = test_info[0],
                section_id = test_info[1],
                start_time=test_info[2],
                end_time=test_info[3]
            )
            return test
