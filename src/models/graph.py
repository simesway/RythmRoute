import networkx as nx
from threading import Lock
from src.database.db import SessionLocal
from src.database.models import RelationshipTypeEnum, Genre
from src.database.selects import get_all_mb_genres, get_all_relationships



class GenreGraph:
  G = nx.DiGraph()
  lock = Lock()
  subgraphs = {}

  def __init__(self, subgraph_type=None):
    self.subgraph_type = subgraph_type

  def __enter__(self):
    graph = self.G if self.subgraph_type is None else self.subgraphs[self.subgraph_type]
    self.lock.acquire()
    return graph

  def __exit__(self, exc_type, exc_value, traceback):
    self.lock.release()
    return False

  @staticmethod
  def compute_weight(genre1: Genre, genre2: Genre):
    if genre1.bouncy_value and genre2.bouncy_value:
      return ((genre1.bouncy_value - genre2.bouncy_value)**2 + (genre1.organic_value - genre2.organic_value)**2)**0.5
    else:
      return 0

  @classmethod
  def initialize(cls):
    with SessionLocal() as session:
      genres = get_all_mb_genres(session)
      relationships = get_all_relationships(session)

    bouncy_vals = [genre[0].bouncy_value for genre in genres if genre[0].bouncy_value]
    organic_vals = [genre[0].organic_value for genre in genres if genre[0].organic_value]

    # Find the min and max for x and y
    b_min, b_max = min(bouncy_vals), max(bouncy_vals)
    o_min, o_max = min(organic_vals), max(organic_vals)

    with cls.lock:
      for genre in genres:
        genre = genre[0]
        b = (genre.bouncy_value - b_min) / (b_max - b_min) if genre.bouncy_value else None
        o = (genre.organic_value - o_min) / (o_max - o_min) if genre.organic_value else None
        cls.G.add_node(
          genre.id,
          name=genre.name,
          bouncy_value=b,
          organic_value=o
        )

      for rel in relationships:
        rel = rel[0]
        g1 = next((genre[0] for genre in genres if genre[0].id == rel.genre1_id), None)
        g2 = next((genre[0] for genre in genres if genre[0].id == rel.genre2_id), None)
        weight = cls.compute_weight(g1, g2) if g1 and g2 else 0
        cls.G.add_edge(rel.genre2_id, rel.genre1_id, weight=weight, type=rel.relationship.value)

      cls._initialize_subgraphs()

      nx.freeze(cls.G)

    G = cls.subgraph(RelationshipTypeEnum.SUBGENRE_OF.value)
    for node in cls.G.nodes():
      cls.G.nodes[node]["has_subgenres"] = node in G.nodes and any(G.successors(node))

  @classmethod
  def _initialize_subgraphs(cls):
    cls.subgraphs.clear()
    edge_types = [relationship.value for relationship in RelationshipTypeEnum]
    for edge_type in edge_types:
      nodes = {
                u for u, v, d in cls.G.edges(data=True) if d.get("type") == edge_type
              } | {
                v for u, v, d in cls.G.edges(data=True) if d.get("type") == edge_type
              }

      subgraph = cls.G.subgraph(nodes).copy()
      cls.subgraphs[edge_type] = subgraph

  @classmethod
  def subgraph(cls, graph_type):
    """ Context manager to switch to a specific edge type subgraph. """
    if graph_type not in cls.subgraphs:
      return None

    return cls.subgraphs[graph_type]

  @classmethod
  def shortest_path(cls, start, end, edge_type: RelationshipTypeEnum):
    """Find shortest path using only a specific edge type."""
    subgraph = cls.subgraph(edge_type)
    try:
      return nx.shortest_path(subgraph, source=start, target=end)
    except nx.NetworkXNoPath:
      return None


GenreGraph.initialize()