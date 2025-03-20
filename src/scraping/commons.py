import requests
from bs4 import BeautifulSoup


def get_soup(url: str) -> BeautifulSoup:
  try:
    response = requests.get(url)
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return None

  return BeautifulSoup(response.text, 'html.parser')
