from src.database.model.scraper import collect_every_noise, collect_musicbrainz


def main () -> None:
  collect_every_noise(genre_map=True)
  collect_musicbrainz()

if __name__ == '__main__':
  main()