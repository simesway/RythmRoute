from abc import ABC, abstractmethod

from src.models.SessionData import SessionData


class ArtistSamplingStrategy(ABC):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    """Must be implemented by subclasses."""
    pass


class UniformArtistSampling(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass

class PoissonArtistSampling(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass

class StratifiedArtistSampling(ArtistSamplingStrategy):
  @abstractmethod
  def sample_artists(self, session: SessionData):
    pass