from fastapi import FastAPI
from fastapi.routing import APIRouter
from auth.api import auth_router

app = FastAPI()

web = APIRouter(
    prefix='/web'
)
web.include_router(auth_router, tags=['Test'])

app.include_router(web)
