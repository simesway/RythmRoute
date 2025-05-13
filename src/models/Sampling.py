from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional, Any, Union, Literal
import math
import numpy as np

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

FilterTypes = Union[AttributeFilter, CombinedFilter]

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
  alpha: float = 1.0
  mode: Literal["rank", "log", "softmax"] = "rank"

  def sample(self, items):
    if self.mode == "log":
      return self.log(items)
    elif self.mode == "softmax":
      return self.softmax(items)
    else:
      return self.rank_based(items)

  def log(self, items):
    weights = [math.log(getattr(item, self.attr) + 1e-6) for item in items]
    weights = weights if self.higher_is_better else [1 / (v + 1e-6) for v in weights]
    return random.choices(items, weights=weights, k=1)[0]

  def softmax(self, items):
    vals = np.array([getattr(item, self.attr) for item in items])
    vals = vals if self.higher_is_better else -vals
    exp_vals = np.exp(vals - np.max(vals))  # for numerical stability
    weights = exp_vals / np.sum(exp_vals)
    return random.choices(items, weights=weights, k=1)[0]

  def rank_based(self, items):
    attr_values = np.array([getattr(item, self.attr) for item in items])
    sorted_indices = np.argsort(attr_values)

    if not self.higher_is_better:
      sorted_indices = sorted_indices[::-1]  # Reverse if needed

    sorted_items = [items[i] for i in sorted_indices]
    weights = (np.arange(1, len(sorted_items) + 1) ** self.alpha).tolist()
    return random.choices(sorted_items, weights=weights, k=1)[0]

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return self.sample(items)

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

SamplingStrategyType = Union[
  RandomSampling,
  WeightedSampling,
  AttributeWeightedSampling,
  WeightedCombinedSampler
]