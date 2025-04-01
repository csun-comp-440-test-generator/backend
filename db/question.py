import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv

from db.client import get_db_session

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    id: int
    test_id: int
    question_text: str

dotenv.load_dotenv()

router = APIRouter(prefix="/test/question")

@router.post("/create", status_code=status.HTTP_201_CREATED,tags=["exam","questions"])
async def create_question(question_id:int,test_id:int, question_text:str, tags=["exam","questions"]):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            #Create Pydantic Model
            question = Question(id=question_id,test_id=test_id,question_text=question_text)
            #Create Query
            insert_query = "INSERT INTO question (id,test_id,question_text) VALUES (%s,%s,%s)"
            #Insert into DB
            await cur.execute(insert_query,
                              (question.id,
                               question.test_id,
                               question.question_text,
                               ))
        await conn.commit()
        return question
        
@router.get("/retrieve_questions_by_test_id", status_code=status.HTTP_200_OK, tags=["exam","questions"])
async def get_questions_by_test_id(test_id: int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM question WHERE test_id = %s"
            await cur.execute(
                select_query,
                (test_id,)
                )
            results = await cur.fetchall()
            questions=[]
            for i in range(len(results)):
                question_info = results[i]
                question = Question(
                            id = question_info[0],
                            test_id = question_info[1],
                            question_text = question_info[2]
                            )
                questions.append(question)
            return questions
        
@router.get("/retrieve_by_question_id", status_code=status.HTTP_200_OK, tags=["exam","questions"])
async def get_question_by_question_id(test_id: int, question_id:int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM question WHERE test_id = %s AND id = %s"
            await cur.execute(
                select_query,
                (test_id,
                 question_id,))
            results = await cur.fetchall()
            question_info = results[0]
            question = Question(
                        id = question_info[0],
                        test_id = question_info[1],
                        question_text = question_info[2]
                        )
            return question
        
@router.post("/edit_question", status_code=status.HTTP_202_ACCEPTED, tags=["exam","questions"])
async def edit_question(test_id: int, question_id:int, question_text:str):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            update_query = "UPDATE question SET question_text=%s WHERE test_id=%s and id=%s;"
            question = Question(id=question_id,test_id=test_id,question_text=question_text)
            #Update Entry
            await cur.execute(update_query,
                              (question.question_text,
                               question.test_id,
                               question.id,
                               ))
            await conn.commit()
            return question
