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
from fastapi.middleware.cors import CORSMiddleware

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

# Allow all origins (you can be more specific with a list of domains if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can specify domains like ['http://localhost:3000']
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

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