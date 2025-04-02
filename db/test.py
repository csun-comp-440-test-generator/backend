import sys
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import Test
from db.models import Question
from db.models import Answer

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/test")

@router.post("/create_blank", status_code=status.HTTP_201_CREATED, tags=["exam"])
async def create_blank_test(section_id:int, test_name:str):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Pydantic Model
                test = Test(section_id=section_id,name=test_name)
                #Create Query
                insert_query = "INSERT INTO test (section_id,name) VALUES (%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (test.section_id,
                                test.name,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return test
    
@router.get("/generate_test_questions_from_bank", status_code=status.HTTP_200_OK, tags=["exam"])
async def generate_test_questions_from_bank(section_id:int, test_id:int, number_of_questions:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:           
                test_query = """
                    WITH question_count AS (
                        SELECT COUNT(DISTINCT q.id) AS total_questions
                        FROM test_generation_model.test t 
                        JOIN test_generation_model.question q ON q.test_id = t.id
                        WHERE t.id = %s
                    )
                    SELECT 
                        t.name as test_name,
                        q.id AS question_id,
                        q.question_text AS question_text,
                        a.id AS answer_id,
                        a.answer_text AS answer_text,
                        a.is_correct,
                        qc.total_questions
                    FROM test_generation_model.test t
                    JOIN test_generation_model.question q ON q.test_id = t.id
                    JOIN test_generation_model.answer a ON a.question_id = q.id
                    JOIN question_count qc ON 1=1
                    WHERE t.id = %s;
                    """
                await cur.execute(
                    test_query,
                    (test_id,test_id,)
                    )
                results = await cur.fetchall()
                if number_of_questions > results[0][6]:
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="There are not enough questions in the bank")
                    return

                test_model = None
                question_data = {}
                for row in results:
                    test_name,question_id, question_text,answer_id,answer_text,correct, total_questions = row

                    if test_model is None:
                        test_model = Test(id=test_id,section_id=section_id,name=test_name)
                    
                    if question_id not in question_data:
                        question_data[question_id]=Question(id=question_id,test_id=test_id,question_text=question_text)
                    
                    if question_data[question_id].answers is None:
                        question_data[question_id].answers = []
                        
                    answer = Answer(id=answer_id,test_id=test_id,question_id=question_id,answer_text=answer_text,is_correct=bool(correct))

                    question_data[question_id].answers.append(answer)
                
                question_bank = random.sample(range(1,len(question_data)),number_of_questions)

                filtered_questions = [question_data[i] for i in question_bank if i in question_data]

                #Adds list of Question Models
                if test_model:
                    test_model.questions = filtered_questions
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
                return test_model
        
@router.get("/retrieve_by_section_id", status_code=status.HTTP_200_OK, tags=["exam"])
async def get_tests_by_section_id(section_id: int):
    try:
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
                        name=test_info[2],
                        start_time=test_info[3],
                        end_time=test_info[4]
                    )
                    tests.append(test)
    except Error as err:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return tests
        
@router.get("/retrieve_by_test_id", status_code=status.HTTP_200_OK, tags=["exam"])
async def get_tests_by_test_id(test_id: int, section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                test_query = """
                    SELECT
                        t.name as test_name,
                        q.id as question_id,
                        q.question_text as question_text,
                        a.id as answer_id,
                        a.answer_text as answer_text,
                        a.is_correct
                    FROM test t 
                    JOIN question q on q.test_id = t.id
                    JOIN answer a on a.question_id = q.id
                    WHERE t.id=%s"""
                await cur.execute(
                    test_query,
                    (test_id,)
                    )
                results = await cur.fetchall()

                test_model = None
                question_data = {}
                for row in results:
                    test_name,question_id, question_text,answer_id,answer_text,correct = row

                    if test_model is None:
                        test_model = Test(id=test_id,section_id=section_id,name=test_name)
                    
                    if question_id not in question_data:
                        question_data[question_id]=Question(id=question_id,test_id=test_id,question_text=question_text)
                    
                    if question_data[question_id].answers is None:
                        question_data[question_id].answers = []
                        
                    answer = Answer(id=answer_id,test_id=test_id,question_id=question_id,answer_text=answer_text,is_correct=bool(correct))
                    #question_data[question_id]["answers"].append(answer)
                    question_data[question_id].answers.append(answer)

                #Adds list of Question Models
                if test_model:
                    test_model.questions = list(question_data.values())
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
            return test_model
