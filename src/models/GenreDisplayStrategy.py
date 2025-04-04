from abc import ABC, abstractmethod

class DisplayStrategy(ABC):
    @abstractmethod
    def generate_subgraph(self, user_nodes):
        """Must be implemented by subclasses."""
        pass

# Concrete Strategy
class FullSubgraphStrategy(DisplayStrategy):
    def generate_subgraph(self, user_nodes):
        pass