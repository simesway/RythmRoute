from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Literal, Optional, Any

import random

### FILTERING

class Filter(BaseModel, ABC):
  def __call__(self, items) -> list:
    return self.apply(items)

  @abstractmethod
  def apply(self, items):
    pass


class AttributeFilter(Filter):
  attr: str
  min: Optional[float] = None
  max: Optional[float] = None

  def apply(self, items: list):
    return [
      item for item in items
      if (self.min is None or getattr(item, self.attr) >= self.min)
      and (self.max is None or getattr(item, self.attr) <= self.max)
    ]


class CombinedFilter(Filter):
  filters: List[Filter]

  def apply(self, items: list):
    for f in self.filters:
      items = f(items)
    return items

### SAMPLING

class SamplingStrategy(BaseModel, ABC):
  def __call__(self, items: List[Any], seed: Optional[int] = None) -> list:
    return self.apply(items, seed)

  @abstractmethod
  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    """Must be implemented by subclasses."""
    pass


class RandomSampling(SamplingStrategy):
  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return random.choice(items)

class WeightedSampling(SamplingStrategy):
  weights: Optional[List[float]] = None

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return random.choices(items, weights=self.weights, k=1)[0]

class AttributeWeightedSampling(SamplingStrategy):
  attr: str
  higher_is_better: bool

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    values = [getattr(item, self.attr) for item in items]
    weights = values if self.higher_is_better else [1 / (v + 1e-6) for v in values]
    return random.choices(items, weights=weights, k=1)[0]

class WeightedCombinedSampler(SamplingStrategy):
  samplers: List[SamplingStrategy]
  weights: Optional[List[float]] = None
  n_samples: int = 1

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    result = []
    for i in range(self.n_samples):
      sampler: SamplingStrategy = random.choices(self.samplers, weights=self.weights, k=1)[0]
      result.append(sampler.apply(items, seed))
    return result