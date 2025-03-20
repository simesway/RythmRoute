import re
from urllib.parse import parse_qs, urlparse
from src.database.models import Genre
from src.scraping.commons import get_soup
from src.scraping.helper import normalize_genre_name

countries = "https://everynoise.com/countries.html"


def get_id_from_url(url):
  query_params = parse_qs(urlparse(url).query)
  return query_params.get("id", [None])[0]




def get_genre_page_url(genre_name: str) -> str:
  g_clean = "".join(re.sub(r'[^a-zA-Z0-9]', '', word) for word in genre_name.split())
  return f"https://everynoise.com/engenremap-{g_clean}.html"


def get_countries_dataframe():
  countries_url = "https://everynoise.com/countries.html"
  countries_soup = get_soup(countries_url)

  total_count = 0
  for column in countries_soup.find_all('td', class_='column'):
    country_soup = column.find(class_='country')
    if country_soup is None:
      break
    if country_soup.find("a"):
      name = country_soup.find("a").text
    else:
      name = country_soup.find("span").text
    genre_count = int(country_soup.find(class_='count').text)
    total_count += genre_count
    print(f"{name} | {genre_count}")

    for genre_soup in column.find_all("a", recursive=False):
      print("  ", genre_soup.text)
  print("total_count:",total_count)

def get_top_left_from_style_str(style_str):
  top = re.search(r'top:\s*(\d+)px', style_str)
  left = re.search(r'left:\s*(\d+)px', style_str)
  top = int(top.group(1)) if top else None
  left = int(left.group(1)) if left else None
  return top, left

def get_every_sp_genre():
  genre_map_url = "https://everynoise.com/engenremap.html"
  genre_map_url_soup = get_soup(genre_map_url).find(class_="canvas", role="main")

  genres = []
  for genre in genre_map_url_soup.find_all('div', class_='genre'):
    style_string = genre["style"]
    top, left = get_top_left_from_style_str(style_string)
    name = genre.text[:-2].strip()
    genre = Genre(name=name,
                  normalized_name=normalize_genre_name(name)[0],
                  organic_value=top,
                  bouncy_value=left)
    genres.append(genre)

  return genres

def get_artists_from_genre_page(genre_url):
  genre_soup = get_soup(genre_url).find(class_="canvas")
  artists = genre_soup.find_all('div', class_='genre')
  dicts = []
  for artist in artists:
    name = artist.find_all(string=True, recursive=False)[0]
    top, left = get_top_left_from_style_str(artist["style"])
    sp_id = get_id_from_url(artist.a['href'])
    dicts.append({"name": name,
                  "organic_value": top,
                  "bouncy_value": left,
                  "spotify_id": sp_id})

  return dicts
