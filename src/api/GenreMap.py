import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from src.database.db import SessionLocal
from src.database.models import RelationshipTypeEnum, Genre
from src.database.selects import get_all_genre_relationships, get_related_genres, get_subgenres


class GenreMap():
  def __init__(self):
    self.G = nx.Graph()
    self.pos = graphviz_layout(self.G, prog='neato')

    self.genres: dict = {}


  def add_subgenres(self, genre_id):
    with SessionLocal() as session:
      genres = get_subgenres(session, genre_id)

    for genre in genres:
      g, rel_type = genre
      self._add_genre(g)
      self.G.add_edge(genre_id, g.id, type=rel_type)

    self.update_graph()

  def add_genre(self, genre_id):
    with SessionLocal() as session:
      genre = session.query(Genre).get(genre_id)

    if not genre:
      return False

    self._add_genre(genre)
    self.update_graph()

  def _add_genre(self, genre: Genre):
    self.G.add_node(genre.id, label=genre.name)
    self.genres[genre.id] = genre

  def update_graph(self):
    self.pos = graphviz_layout(self.G, prog='neato')

  def draw_graph(self):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(15, 15))
    nx.draw(self.G, self.pos, with_labels=True, node_color='lightblue', node_size=700, font_size=16)
    plt.title("GenreMap")
    plt.show()

  def get_json(self):
    #centrality = nx.eigenvector_centrality(self.G)
    #print(centrality)
    genres = {
      genre_id: {"name": self.genres[genre_id].name,
                 "x": float(self.pos[genre_id][0]),
                 "y": float(self.pos[genre_id][1]),
                 "r": 10}
      for genre_id in self.G.nodes
    }
    relationships = [{"source": e[0], "target": e[1], "type": self.G.edges[e]["type"]} for e in self.G.edges]
    return {"genres": self.scale_genre_coordinates(genres), "relationships": relationships}

  def scale_genre_coordinates(self, genres: dict):
    # Base case: no genres
    if not genres:
      return {}

    # Base case: only one genre
    if len(genres) == 1:
      genre_id, genre = next(iter(genres.items()))
      return {
        genre_id: {
          "name": genre["name"],
          "x": 0.5,  # Default scaled value
          "y": 0.5  # Default scaled value
        }
      }

    # Extract x and y coordinates
    x_coords = [genre['x'] for genre in genres.values()]
    y_coords = [genre['y'] for genre in genres.values()]

    # Find the min and max for x and y
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)



    scaled_genres = {
      genre_id: {
        "name": genre["name"],
        "r": genre["r"],
        "x": (genre['x'] - x_min) / (x_max - x_min),
        "y": (genre['y'] - y_min) / (y_max - y_min)
      }
      for genre_id, genre in genres.items()
    }

    return scaled_genres

