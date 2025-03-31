import dotenv
from db.test import router as testRouter
import uvicorn as uv

from fastapi import FastAPI, Form

dotenv.load_dotenv()

app = FastAPI()
app.include_router(testRouter)

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")