import datetime
from pydantic import BaseModel
from typing import Optional
from typing import List


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
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    questions:Optional[List[Question]] = None