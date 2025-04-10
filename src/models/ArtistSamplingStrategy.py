from abc import ABC, abstractmethod

from src.models.SessionData import SessionData


class ArtistSamplingStrategy(ABC):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    """Must be implemented by subclasses."""
    pass


class UniformArtistSamplingStrategy(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass

class PoissonArtistSamplingStrategy(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass

class StratifiedArtistSamplingStrategy(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass