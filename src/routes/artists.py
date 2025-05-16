from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.models.ObjectSampling import AttributeWeightedSampling
from src.models.create_SessionResponse import create_SessionResponse
from src.models.SessionData import SessionData
from src.core.SpotifyCache import SpotifyCache
from src.core.session_manager import get_session, store_session

router = APIRouter(prefix="/artists", default_response_class=JSONResponse)

@router.post("/sample/{genre_id}")
async def sample_artists(genre_id: int, sampler: AttributeWeightedSampling, session: SessionData = Depends(get_session)):
  session.factory.sample_artists(genre_id, sampler)
  await store_session(session)
  return await create_SessionResponse(session)

@router.get("/album/{artist_id}")
async def get_artist(artist_id: str):
  tracks = SpotifyCache().get_album_tracks(artist_id)
  return tracks

@router.get("/releases/{artist_id}")
async def get_releases(artist_id: str):
  return SpotifyCache().get_releases(artist_id)

@router.get("/top_tracks/{artist_id}")
async def get_releases(artist_id: str):
  return SpotifyCache().get_top_tracks(artist_id)
