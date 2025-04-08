from src.scraping.commons import get_soup
from src.database.models import Genre, GenreRelationship, RelationshipTypeEnum
import re
from typing import Optional, List

from src.scraping.helper import normalize_genre_name

GENRE_LIST = "https://musicbrainz.org/genres"


def get_genre_page_url(mb_id: str) -> str:
  return f"https://musicbrainz.org/genre/{mb_id}"

def get_mb_id_from_href(href: str) -> Optional[str]:
  match = re.search(r'/genre/([a-f0-9\-]+)', href)

  if match:
    genre_id = match.group(1)
    return genre_id
  return None

def get_genres() -> List[Genre]:
  genre_list = get_soup(GENRE_LIST).find("div", id="page").find("div", id="content")
  genres = []
  for list_item in genre_list.find_all("li"):
    a = list_item.find("a")
    name = a.text
    genre = Genre(
      name=name,
      normalized_name=normalize_genre_name(name)[0],
      mb_id=get_mb_id_from_href(a["href"])
    )
    genres.append(genre)
  return genres

def get_genre_page(url: str, mb_id: str=""):
  if not mb_id == "":
    url = get_genre_page_url(mb_id)

  soup = get_soup(url).find("div", id="content")

  tables = soup.find_all("table", class_="details")
  relationships = []

  for table in tables:
    for row in table.find_all("tr"):
      relationship_type = row.find("th").text.strip()
      related_genres = [a.text.strip() for a in row.find("td").find_all("a")]

      for genre in related_genres:
        if relationship_type == "subgenre of:":
          relationships.append((genre, "subgenre of"))
        elif relationship_type == "subgenres:":
          relationships.append((genre, "subgenre"))
        elif relationship_type == "fusion of:":
          relationships.append((genre, "fusion of"))
        elif relationship_type == "has fusion genres:":
          relationships.append((genre, "fusion genre"))
        elif relationship_type == "influenced by:":
          relationships.append((genre, "influenced by"))
        elif relationship_type == "influenced genres:":
          relationships.append((genre, "influenced genre"))

  return relationships