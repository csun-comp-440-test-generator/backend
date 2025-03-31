import dotenv
from client import router as clientRouter
import uvicorn as uv

from fastapi import FastAPI, Form

dotenv.load_dotenv()

app = FastAPI()
app.include_router(clientRouter)

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")