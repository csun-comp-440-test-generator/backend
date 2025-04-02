import dotenv
from db.test import router as testRouter
from db.question import router as questionRouter
from db.answer import router as answerRouter
from db.course import router as courseRouter
from db.teacher import router as teacherRouter
from db.student import router as studentRouter
from db.section import router as sectionRouter

import uvicorn as uv

from fastapi import FastAPI, Form

dotenv.load_dotenv()

tags_metadata = [
    {
        "name": "exam",
        "description": "Operations used for exam creation.",
    },
    {
        "name": "questions",
        "description": "Operations used for created and editing questions.",
    },
    {
        "name": "answers",
        "description": "Operations used for created and editing answers.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(testRouter)
app.include_router(questionRouter)
app.include_router(answerRouter)
app.include_router(courseRouter)
app.include_router(teacherRouter)
app.include_router(studentRouter)
app.include_router(sectionRouter)

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")