from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.models.ObjectSampling import SamplingConfig
from src.models.SongSampler import CombinedSamplerConfig, StrategyWeightPair, RandomReleaseConfig
from src.models.create_SessionResponse import create_SessionResponse
from src.models.SessionData import SessionData
from src.core.session_manager import get_session, store_session

router = APIRouter(prefix="/sample", default_response_class=JSONResponse)

@router.post("/artists/{genre_id}")
async def sample_artists(genre_id: int, config: SamplingConfig, session: SessionData = Depends(get_session)):
  print(config.model_dump_json(indent=2))
  session.factory.sample_artists(genre_id, config)
  await store_session(session)
  return await create_SessionResponse(session)

@router.post("/tracks/{genre_id}")
async def sample_artists(genre_id: int, request: Request, session: SessionData = Depends(get_session)):
    data = await request.json()
    sampler = CombinedSamplerConfig.model_validate(data['sampler'])  # full manual parsing
    if not sampler.strategies:
        sampler.strategies.append(StrategyWeightPair(strategy=RandomReleaseConfig(), weight=1))

    session.factory.sample_tracks(genre_id, sampler)
    await store_session(session)
    return await create_SessionResponse(session)
