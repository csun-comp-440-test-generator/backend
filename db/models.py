import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, List, Annotated

#For Retrieving data and SQL
class Answer(BaseModel):
    id: Optional[int] = None
    test_id: int
    question_id :int
    answer_text: str
    is_correct: bool

class Question(BaseModel):
    id: int
    test_id: int
    question_text: str
    answers:Optional[List[Answer]] = None


class Test(BaseModel):
    id: Optional[int] = None
    section_id: int
    name:str
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    questions:Optional[List[Question]] = None

#For Sending Data
class AnswerBank(BaseModel):
    answer_text:str
    is_correct:bool

class QuestionBank(BaseModel):
    question_text:str
    answers:List[AnswerBank]


class ExamBank(BaseModel):
    section_id:int
    exam_name:str
    questions:List[QuestionBank]
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None


class Course(BaseModel):
    id: int
    name: str

class Section(BaseModel):
    id: int
    course: int
    course_name: Optional[str] = None
    teacher:int
    teacher_name:Optional[str] = None
    assistant: Optional[int] = None
    assistant_name: Optional[int] = None

class Teacher(BaseModel):
    id: Optional[int] = None
    name: str
    email:str

class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email:str



class SectionInfoRequest(BaseModel):
    course_id:  int
    section_id :int
    course_name: str
    assistant_id: Optional[int] = None

class TestInfoRequest(BaseModel):
    test_id:  int
    test_name: str


class TestSubmission(BaseModel):
    student_id:int
    test_id:int
    attempt:int
    score: Decimal
    submission_time:Optional[datetime.datetime] = None

class RecieveSubmission(BaseModel):
    student_id:int
    test_id:int
    attempt:int
    score: Decimal