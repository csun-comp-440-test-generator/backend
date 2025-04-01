import dotenv
from db.test import router as testRouter
from db.question import router as questionRouter
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
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(testRouter)
app.include_router(questionRouter)

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")