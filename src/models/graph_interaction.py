from src.models.session_data import SessionData


def toggle_genre_expansion(session: SessionData, genre_id: int) -> SessionData:
  if genre_id in session.genres.expanded:
    session.genres.expanded.remove(genre_id)
  else:
    session.genres.expanded.append(genre_id)

  return session

def toggle_genre_selection(session: SessionData, genre_id: int) -> SessionData:
  if genre_id in session.genres.selected:
    session.genres.selected.remove(genre_id)
  else:
    session.genres.selected.append(genre_id)

  return session