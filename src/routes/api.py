from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.routes import graph, artists, playlist, sample

router = APIRouter(prefix="/api", default_response_class=JSONResponse)

router.include_router(graph.router)

router.include_router(artists.router)

router.include_router(playlist.router)

router.include_router(sample.router)