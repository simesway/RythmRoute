import unicodedata

def normalize_string(string: str) -> str:
  return string.strip().lower()


def normalize_genre_name(genre: str):
  genre = unicodedata.normalize("NFKD", genre)  # Decompose accents
  genre = "".join(c for c in genre if not unicodedata.combining(c))  # Remove accents
  genre = genre.lower().strip()  # Normalize case & trim spaces
  genre_spaces = genre.replace("-", " ")  # Replace hyphens with spaces
  genre_hyphens = genre.replace(" ", "-")  # Replace spaces with hyphens
  return genre_spaces, genre

print(normalize_genre_name("nueva canción lo-fi hip höp"))