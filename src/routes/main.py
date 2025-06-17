from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
import logging

from src.core.session_manager import get_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home(session=Depends(get_session)):
    with open("src/templates/home.html") as f:
        return f.read()

@router.get("/testing", response_class=HTMLResponse)
def new_home():
    with open("src/templates/new_home.html") as f:
        return f.read()