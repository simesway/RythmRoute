from abc import ABC, abstractmethod
from networkx.drawing.nx_agraph import graphviz_layout

import networkx as nx
from networkx.readwrite import json_graph
from typing import List

from src.database.models import RelationshipTypeEnum
from src.models.graph import GenreGraph
from src.models.session_data import SessionData


class DisplayStrategy(ABC):
  @abstractmethod
  def generate_subgraph(self, session: SessionData):
    """Must be implemented by subclasses."""
    pass

  def generate_data(self) -> dict:
    return dict()

  def generate_layout(self, graph):
    return graphviz_layout(graph, prog="neato")

  def get_json_layout(self, graph):
    if not graph.nodes:
      return {}

    if len(graph.nodes) == 1:
      return {graph.nodes[0]: (0.5, 0.5)}

    layout = self.generate_layout(graph)
    return self.normalize_layout(layout)

  def to_json(self, session: SessionData):
    subgraph = self.generate_subgraph(session)

    node_edges = json_graph.node_link_data(subgraph)
    layout = self.get_json_layout(subgraph)
    data = self.generate_data()
    return {"graph": node_edges, "layout": layout, "data": data}

  @staticmethod
  def normalize_layout(layout: dict) -> dict:
    x_coords = [genre[0] for genre in layout.values()]
    y_coords = [genre[1] for genre in layout.values()]

    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    return {
      node_id:
        {"x": (x - x_min) / (x_max - x_min),
         "y": (y - y_min) / (y_max - y_min)}
      for node_id, (x, y) in layout.items()}



class StartingGenresStrategy(DisplayStrategy):
  #starting_genres = {1, 3, 5, 20, 99, 114, 151, 379, 523, 6598, 1804}
  starting_genres = set(GenreGraph.roots)

  @classmethod
  def initialize_starting_genres(cls):
    genres = list(cls.starting_genres)
    inter_genres = cls.get_subgenres_between(
      genres, genres,
      RelationshipTypeEnum.SUBGENRE_OF.value)
    cls.starting_genres = cls.starting_genres.union(inter_genres)

  @staticmethod
  def get_subgenres_between(source: list[int], target: list[int], graph_type=None) -> set[int]:
    nodes = set()
    for source_id in source:
      for target_id in target:
        with GenreGraph(graph_type) as G:
          try:
            path = nx.shortest_path(G, source=source_id, target=target_id)
          except Exception as e:
            path = []
          nodes = nodes | set(path)
    return nodes

  @staticmethod
  def prune_descendants(graph: nx.DiGraph, expanded: set[int], nodes: set[int]) -> set[int]:
    all_descendants = set()
    for node in set(graph.nodes()) - expanded:
      stack = [node]
      while stack:
        current = stack.pop()
        if current in all_descendants:
          continue
        all_descendants.add(current)
        stack.extend(graph.successors(current))
    return nodes - all_descendants

  def generate_subgraph(self, session: SessionData):

    selected = set(session.genres.selected or [])
    expanded = set(session.genres.expanded or [])

    all_nodes = self.starting_genres | selected

    # Add subgenres between starting genres
    all_nodes |= self.get_subgenres_between(
      list(all_nodes), list(all_nodes), RelationshipTypeEnum.SUBGENRE_OF.value
    )

    # Add paths from starting genres to selected genres
    if selected:
      all_nodes |= self.get_subgenres_between(
        list(self.starting_genres), list(selected), RelationshipTypeEnum.SUBGENRE_OF.value
      )

    # Add children of expanded nodes
    with GenreGraph(RelationshipTypeEnum.SUBGENRE_OF.value) as G:
      for node in expanded:
        if G.has_node(node):
          all_nodes.update(G.successors(node))

      self.prune_descendants(G, expanded, all_nodes)

    with GenreGraph() as G:
      return G.subgraph(all_nodes)

StartingGenresStrategy.initialize_starting_genres()
