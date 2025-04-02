import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from threading import Lock

from networkx.readwrite import json_graph
from typing import Optional

import json

from src.database.db import SessionLocal
from src.database.models import Genre, RelationshipTypeEnum
from src.database.selects import get_all_mb_genres, get_all_relationships


# Global graph instance + lock for safe access
G = nx.Graph()
lock = Lock()


def add_genre(genre: Genre):
  global G


def add_relationship(genre1: Genre, rel_type: RelationshipTypeEnum, genre2: Genre):
  global G
  G.add_edge(genre1.id, genre2.id, type=rel_type)

def load_graph():
  global G

  with SessionLocal() as session:
    genres = get_all_mb_genres(session)
    relationships = get_all_relationships(session)

  bouncy_vals = [genre[0].bouncy_value for genre in genres if genre[0].bouncy_value]
  organic_vals = [genre[0].organic_value for genre in genres if genre[0].organic_value]

  # Find the min and max for x and y
  b_min, b_max = min(bouncy_vals), max(bouncy_vals)
  o_min, o_max = min(organic_vals), max(organic_vals)

  for genre in genres:
    genre = genre[0]
    b = (genre.bouncy_value - b_min) / (b_max - b_min) if genre.bouncy_value else None
    o = (genre.organic_value - o_min) / (o_max - o_min) if genre.organic_value else None
    G.add_node(
      genre.id,
      label=genre.name,
      bouncy_value=b,
      organic_value=o,
    )

  for rel in relationships:
    rel = rel[0]
    G.add_edge(rel.genre1_id, rel.genre2_id, type=rel.relationship.value)

  nx.freeze(G)

load_graph()

def get_neighbors(node):
    """Thread-safe retrieval of neighbors."""
    with lock:
        if node in G:
            return list(G.neighbors(node))
        return []

def get_layout(graph: nx.Graph) -> dict:
  if not graph.nodes:
    return {}

  if len(graph.nodes) == 1:
    return {graph.nodes[0]: (0.5, 0.5)}

  layout = graphviz_layout(graph, prog='neato')

  x_coords = [genre[0] for genre in layout.values()]
  y_coords = [genre[1] for genre in layout.values()]

  x_min, x_max = min(x_coords), max(x_coords)
  y_min, y_max = min(y_coords), max(y_coords)

  scaled = {}
  for id, (x, y) in layout.items():
    scaled[id] = {"x": (x - x_min) / (x_max - x_min), "y": (y - y_min) / (y_max - y_min)}

  return scaled


def to_json(graph: Optional[nx.Graph]):
  if graph is None:
    global G
  else:
    G = graph

  node_edges = json_graph.node_link_data(G)
  layout = get_layout(G)
  return {"node_edges": node_edges, "layout": layout}