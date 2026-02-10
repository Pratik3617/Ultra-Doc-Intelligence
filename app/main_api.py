from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Ultra Doc Intelligence API",
    version="1.0"
)

app.include_router(router)
