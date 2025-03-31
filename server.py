from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routes import api, spotify, main, session

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(main.router)

app.include_router(session.router)

app.include_router(api.router)

app.include_router(spotify.router)
