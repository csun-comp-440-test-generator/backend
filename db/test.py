from decimal import Decimal
import sys
from typing import Annotated, List

from pydantic import BaseModel, Field
# sys hacks to get imports to work
sys.path.append("./")

import os
import dotenv
import datetime
import random

from db.client import get_db_session
from db.models import RecieveSubmission, Test, TestSubmission
from db.models import Question
from db.models import Answer
from db.models import ExamBank

from fastapi import APIRouter, status, HTTPException
from mysql.connector import Error

dotenv.load_dotenv()

router = APIRouter(prefix="/test", tags=["exam"])

@router.post("/create_test", status_code=status.HTTP_201_CREATED, tags=["exam"])
async def create_test(exam:ExamBank):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                #Create Pydantic Model
                #Insert Test Info
                # if exam.start_time == None and exam.end_time == None:
                #     exam_info = Test(section_id=exam.section_id,name=exam.exam_name)
                #     #Create Query
                #     insert_query = "INSERT INTO test (section_id,name) VALUES (%s,%s)"
                #     #Insert into DB
                #     await cur.execute(insert_query,
                #                     (exam_info.section_id,
                #                     exam_info.name,))
                #     test_id = cur.lastrowid
                #     total_questions = 0
                # else:
                exam_info = Test(
                    section_id=exam.section_id,
                    name=exam.exam_name, 
                    max_questions=exam.max_questions,
                    start_time=exam.start_time,
                    end_time=exam.end_time,)
                #Create Query
                insert_query = "INSERT INTO test (section_id,name, start_time, end_time,max_questions) VALUES (%s,%s,%s,%s,%s)"
                #Insert into DB
                await cur.execute(insert_query,
                                (exam_info.section_id,
                                exam_info.name,
                                exam_info.start_time,
                                exam_info.end_time,
                                exam_info.max_questions))
                test_id = cur.lastrowid
                total_questions = 0

                for question in exam.questions:
                    total_questions += 1
                    newQuestion = Question(id=total_questions,test_id=test_id,question_text=question.question_text)
                    insert_query = "INSERT INTO question (id,test_id,question_text) VALUES (%s,%s,%s)"
                    #Insert into DB
                    await cur.execute(insert_query,
                                    (newQuestion.id,
                                    newQuestion.test_id,
                                    newQuestion.question_text,
                                    ))

                    for answer in question.answers:
                        newAnswer = Answer(test_id=test_id,question_id=total_questions,answer_text=answer.answer_text,is_correct=answer.is_correct)
                        insert_query = "INSERT INTO answer (test_id,question_id,answer_text,is_correct) VALUES (%s,%s,%s,%s);"
                        await cur.execute(insert_query,
                                        (newAnswer.test_id,
                                        newAnswer.question_id,
                                        newAnswer.answer_text,
                                        int(newAnswer.is_correct),
                                        ))
            await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return exam

@router.post("/create_blank", status_code=status.HTTP_201_CREATED)
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
    
@router.get("/generate_test_questions_from_bank", status_code=status.HTTP_200_OK)
async def generate_test_questions_from_bank(test_id:int):
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
                        t.section_id as section_id,
                        t.max_questions as max_questions,
                        t.start_time as start_time,
                        t.end_time as end_time,
                        q.id AS question_id,
                        q.question_text AS question_text,
                        a.id AS answer_id,
                        a.answer_text AS answer_text,
                        a.is_correct,
                        qc.total_questions
                    FROM test_generation_model.test t
                    JOIN test_generation_model.question q ON q.test_id = t.id
                    JOIN test_generation_model.answer a ON a.question_id = q.id
                    AND a.test_id = t.id
                    JOIN question_count qc ON 1=1
                    WHERE t.id = %s
                    """
                await cur.execute(
                    test_query,
                    (test_id,test_id,)
                    )
                results = await cur.fetchall()

                test_model = None
                question_data = {}
                for row in results:
                    test_name,section_id,max_questions,start_time,end_time,question_id, question_text,answer_id,answer_text,correct, total_questions = row

                    if test_model is None:
                        test_model = Test(id=test_id,section_id=section_id,name=test_name,max_questions=max_questions, start_time=start_time, end_time=end_time)
                    
                    if question_id not in question_data:
                        question_data[question_id]=Question(id=question_id,test_id=test_id,question_text=question_text)
                    
                    if question_data[question_id].answers is None:
                        question_data[question_id].answers = []
                        
                    answer = Answer(id=answer_id,test_id=test_id,question_id=question_id,answer_text=answer_text,is_correct=bool(correct))

                    question_data[question_id].answers.append(answer)
                

                question_bank = random.sample(range(1,len(question_data)+1),max_questions)

                filtered_questions = [question_data[i] for i in question_bank if i in question_data]

                #Adds list of Question Models
                if test_model:
                    test_model.questions = filtered_questions
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
                return test_model
        
@router.get("/retrieve_by_section_id", status_code=status.HTTP_200_OK)
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
                        end_time=test_info[4],
                        max_questions=test_info[5]
                    )
                    tests.append(test)
    except Error as err:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return tests
    
@router.get("/retrieve_question_count", status_code=status.HTTP_200_OK)
async def get_question_count_by_test_id(test_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                select_query = """
                SELECT COUNT(*) AS question_count
                FROM question
                WHERE test_id = %s;"""
                await cur.execute(
                    select_query,
                    (test_id,)
                    )
                results = await cur.fetchone()
                count = results[0]
    except Error as err:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return count

class ExamInfoRetrieve(BaseModel):
    exam_id: int
    section_id:int
    name:str
    start_time: datetime.datetime
    end_time: datetime.datetime
    max_questions:int

@router.get("/retrieve_info", status_code=status.HTTP_200_OK)
async def get_info_by_id(test_id:int, section_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                select_query = """
                SELECT *
                FROM test
                WHERE id = %s
                AND section_id = %s;"""
                await cur.execute(
                    select_query,
                    (test_id,
                     section_id)
                    )
                results = await cur.fetchone()
                test_info = ExamInfoRetrieve(
                        exam_id=results[0],
                        section_id=results[1],
                        name=results[2],
                        start_time=results[3],
                        end_time=results[4],
                        max_questions = results[5])
    except Error as err:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return test_info

class ExamQuestionRetreival(BaseModel):
    questions: List[Question] | None = None   

@router.get("/retrieve_by_test_id", status_code=status.HTTP_200_OK)
async def get_test_questions_by_id(test_id: int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                test_query = """
                    SELECT
                        q.id as question_id,
                        q.question_text as question_text,
                        a.id as answer_id,
                        a.answer_text as answer_text,
                        a.is_correct
                    FROM test t 
                    JOIN question q on q.test_id = t.id
                    JOIN answer a on a.question_id = q.id
                    AND a.test_id = t.id
                    WHERE t.id=%s"""
                await cur.execute(
                    test_query,
                    (test_id,)
                    )
                results = await cur.fetchall()

                test_model = None
                question_data = {}
                for row in results:
                    question_id, question_text,answer_id,answer_text,correct = row

                    if test_model is None:
                        test_model = ExamQuestionRetreival()
                    
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
    
@router.post("/sumbit_exam", status_code=status.HTTP_200_OK)
async def create_test_submission(submission:RecieveSubmission ):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                submission_time = datetime.datetime.now()
                #Create Pydantic Model
                testSubmission = TestSubmission(
                    student_id=submission.student_id,
                    test_id=submission.test_id,
                    attempt=submission.attempt,
                    score=submission.score,
                    submission_time=submission_time,)
                #Create Query
                insert_query = """
                INSERT INTO test_submission 
                (student_id,test_id,attempt,submission_time,score) 
                VALUES (%s,%s,%s,%s,%s)"""
                #Insert into DB
                await cur.execute(insert_query,(
                            testSubmission.student_id,
                            testSubmission.test_id,
                            testSubmission.attempt,
                            testSubmission.submission_time,
                            testSubmission.score,))
                await conn.commit()
    except Error as err:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
        return testSubmission
    
@router.get("/retrieve_attempts", status_code=status.HTTP_200_OK)
async def get_attempts_by_id(student_id:int, test_id:int):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                select_query = """
                SELECT attempt
                FROM test_submission
                WHERE student_id = %s
                AND test_id = %s;"""
                await cur.execute(
                    select_query,
                    (student_id,
                     test_id,)
                    )
                results = await cur.fetchall()
                if results:
                    attempt = len(results)
                else:
                    attempt = 1
    except Error as err:
        print(f"Error: {err}")#HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Error: {err}")
    else:
         return attempt

class DeleteRequest(BaseModel):
    exam_id:int
    section_id:int

@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_by_id(del_request: DeleteRequest):
    try:
        async for conn in get_db_session():
            async with await conn.cursor() as cur:
                del_query = "DELETE FROM test WHERE id=%s AND section_id = %s;"
                await cur.execute(
                    del_query,
                    (del_request.exam_id,
                     del_request.section_id)
                    )
                await conn.commit()
    except Error as err:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error: {err}")
    else:
        return True