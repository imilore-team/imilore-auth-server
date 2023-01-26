from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.init import engine, DeclarativeBase

from src.routes.auth import router as auth_router


DeclarativeBase.metadata.create_all(bind=engine)
DeclarativeBase.metadata.bind = engine


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?:\/\/.*\.?imilore\.tech",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)