import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv

from db.client import get_db_session
from db.models import Answer

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional

dotenv.load_dotenv()

router = APIRouter(prefix="/test/answer")

@router.post("/create", status_code=status.HTTP_201_CREATED,tags=["answers"])
async def create_answer(test_id:int, question_id:int,answer_text:str,correct:bool):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            #Create Query
            insert_query = "INSERT INTO answer (test_id,question_id,answer_text,is_correct) VALUES (%s,%s,%s,%s)"
            answer = Answer(test_id=test_id,question_id=question_id,answer_text=answer_text,is_correct=correct)
            #Insert into DB
            await cur.execute(insert_query,
                              (answer.test_id,
                               answer.question_id,
                               answer.answer_text,
                               int(answer.is_correct),
                               ))
        await conn.commit()
        return answer
        
@router.get("/retrieve_answers_by_question", status_code=status.HTTP_200_OK, tags=["answers"])
async def get_answers_by_test_id_question_id(test_id:int,question_id: int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM answer WHERE test_id=%s AND question_id = %s"
            await cur.execute(
                select_query,
                (test_id,question_id,)
                )
            results = await cur.fetchall()
            answers=[]
            for i in range(len(results)):
                answer_info = results[i]
                answer = Answer(
                            id = answer_info[0],
                            test_id = answer_info[1],
                            question_id = answer_info[2],
                            answer_text = answer_info[3],
                            is_correct=bool(answer_info[4])
                            )
                answers.append(answer)
            return answers
        
@router.get("/retrieve_by_answer_id", status_code=status.HTTP_200_OK, tags=["answers"])
async def get_answer_by_answer_id(question_id: int, answer_id:int):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            select_query = "SELECT * FROM answer WHERE question_id = %s AND id = %s"
            await cur.execute(
                select_query,
                (question_id,
                 answer_id,))
            results = await cur.fetchall()
            answer_info = results[0]
            answer = Answer(
                        id = answer_info[0],
                        test_id = answer_info[1],
                        question_id = answer_info[2],
                        answer_text = answer_info[3],
                        is_correct=bool(answer_info[4])
                        )
            return answer
        
@router.post("/edit_answer", status_code=status.HTTP_202_ACCEPTED, tags=["answers"])
async def edit_answer(test_id: int, question_id:int, answer_id:int, answer_text:str,correct:bool):
    async for conn in get_db_session():
        async with await conn.cursor() as cur:
            update_query = "UPDATE answer SET answer_text=%s,is_correct=%s WHERE test_id=%s AND question_id=%s AND id=%s;"
            answer = Answer(test_id=test_id,question_id=question_id,id=answer_id,answer_text=answer_text,is_correct=correct)
            #Update Entry
            await cur.execute(update_query,
                              (answer.answer_text,
                               int(answer.is_correct),
                               answer.test_id,
                               answer.question_id,
                               answer.id,
                               ))
            await conn.commit()
            return answer

@router.post("/delete_answer_by_id", status_code=status.HTTP_200_OK, tags=["answers"])
async def delete_answer_by_id(test_id:int,question_id:int,answer_id:int):
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                delete_query="DELETE FROM answer WHERE test_id=%s AND question_id=%s AND id=%s"
                await cur.execute(delete_query,(test_id,question_id,answer_id,))
            await conn.commit()
            return True
        
@router.post("/delete_answer_by_question", status_code=status.HTTP_200_OK, tags=["answers"])
async def delete_answer_by_question_id(test_id:int,question_id:int):
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                delete_query="DELETE FROM answer WHERE test_id=%s AND question_id=%s"
                await cur.execute(delete_query,(test_id,question_id,))
            await conn.commit()
            return True