from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.api.GenreMap import GenreMap

router = APIRouter(prefix="/api", default_response_class=JSONResponse)

genre_map = GenreMap()

@router.get("/genre/{genre_id}")
async def get_subgenres(genre_id: int):
  genre_map.add_genre(genre_id)
  return genre_map.get_json()

@router.get("/subgenres/{genre_id}")
async def get_subgenres(genre_id: int):
  genre_map.add_subgenres(genre_id)
  print(genre_map.genres)
  return genre_map.get_json()

@router.get("/reset")
async def reset():
  global genre_map
  genre_map = GenreMap()
  return genre_map.get_json()


