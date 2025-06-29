from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union, Literal
import numpy as np
import random
import logging


logger = logging.getLogger("ObjectSampling")
logging.basicConfig(level=logging.INFO)

### FILTERING

class Filter(BaseModel, ABC):
  """Abstract base class for filters applied to item lists."""
  def __call__(self, items) -> list:
    return self.apply(items)

  @abstractmethod
  def apply(self, items):
    pass


class AttributeFilter(Filter):
  """Filters items based on an attribute's min/max values."""
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
  """Combines multiple AttributeFilters sequentially."""
  filters: List[AttributeFilter]

  def apply(self, items: list):
    for f in self.filters:
      items = f(items)
    return items

FilterTypes = Union[AttributeFilter, CombinedFilter]

### SAMPLING

class SamplingStrategy(BaseModel, ABC):
  """Abstract base class for sampling strategies."""
  def __call__(self, items: List[Any], seed: Optional[int] = None) -> list:
    return self.apply(items, seed)

  @abstractmethod
  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    """Must be implemented by subclasses."""
    pass


class RandomSampling(SamplingStrategy):
  """Randomly selects one item."""
  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return random.choice(items)

class WeightedSampling(SamplingStrategy):
  """Samples one item based on provided weights."""
  weights: Optional[List[float]] = None

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return random.choices(items, weights=self.weights, k=1)[0]


class AttributeWeightedSampling(SamplingStrategy):
  """Samples items using attribute-based weights."""
  attr: str
  higher_is_better: bool
  alpha: float = 1.0
  mode: Literal["rank", "log", "softmax"] = "rank"

  def sample(self, items):
    if self.mode == "log":
      items, w = self.log(items)
    elif self.mode == "softmax":
      items, w = self.softmax(items)
    else:
      items, w = self.rank_based(items)
    logger.warning("Weights sum to zero; falling back to random choice.")
    return random.choices(items, weights=w, k=1)[0] if sum(w) > 0 else random.choice(items)

  def log(self, items):
    vals = np.array([max(getattr(item, self.attr), 1e-6) for item in items])
    logs = np.log(vals)
    logs = logs if self.higher_is_better else -logs
    weights = np.power(logs, self.alpha)
    return items, weights.tolist()

  def softmax(self, items):
    vals = np.array([getattr(item, self.attr) for item in items])
    vals = vals if self.higher_is_better else -vals
    vals = (vals - np.min(vals)) / (np.ptp(vals) + 1e-8)  # scale to [0,1]
    vals *= self.alpha # sharpen
    exp_vals = np.exp(vals - np.max(vals))  # stability
    weights = exp_vals / np.sum(exp_vals)
    return items, weights.tolist()

  def rank_based(self, items):
    attr_values = np.array([getattr(item, self.attr) for item in items])
    sort_idx = np.argsort(attr_values)
    if not self.higher_is_better:
      sort_idx = sort_idx[::-1]  # Reverse if needed

    sorted_items = [items[i] for i in sort_idx]
    weights = np.power(np.arange(1, len(items) + 1), self.alpha)
    return sorted_items, weights.tolist()

  def apply(self, items: List[Any], seed: Optional[int] = None) -> Any:
    if seed is not None:
      random.seed(seed)
    return self.sample(items)

SamplingStrategyType = Union[
  RandomSampling,
  WeightedSampling,
  AttributeWeightedSampling
]

class WeightedCombinedSampler(SamplingStrategy):
  """Combines multiple AttributeWeightedSamplers with weights."""
  samplers: List[AttributeWeightedSampling]
  weights: Optional[List[float]] = None
  n_samples: int = 1

  def apply(self, items: List[Any], seed: Optional[int] = None) -> List[Any]:
    if seed is not None:
      random.seed(seed)
    logger.info(f"Combined sampling from {len(self.samplers)} samplers.")

    n = len(items)
    combined_weights = np.zeros(n)

    # Normalize sampler weights
    sampler_weights = (
      np.array(self.weights) / sum(self.weights)
      if self.weights else np.ones(len(self.samplers)) / len(self.samplers)
    )

    for sampler, w in zip(self.samplers, sampler_weights):
      if sampler.mode == "log":
        _, weights = sampler.log(items)
        indices = list(range(n))
      elif sampler.mode == "softmax":
        _, weights = sampler.softmax(items)
        indices = list(range(n))
      else:  # rank-based
        sorted_attr = np.array([getattr(item, sampler.attr) for item in items])
        sort_idx = np.argsort(sorted_attr)
        if not sampler.higher_is_better:
          sort_idx = sort_idx[::-1]
        weights = (np.arange(1, n + 1) ** sampler.alpha).tolist()
        indices = sort_idx.tolist()

      weights = np.array(weights)
      if np.sum(weights) > 0:
        weights = weights / np.sum(weights)

      # Map weights back to original item indices
      temp_weights = np.zeros(n)
      for idx, w_val in zip(indices, weights):
        temp_weights[idx] = w_val

      combined_weights += w * temp_weights

    n = min(self.n_samples, len(items))
    if np.sum(combined_weights) == 0:
      logger.warning("Combined weights sum to zero; falling back to random sample.")
      return random.sample(items, n)
    else:
      probs = combined_weights / np.sum(combined_weights)
      indices = np.random.choice(len(items), size=n, replace=False, p=probs)
      return [items[i] for i in indices]


class SamplingConfig(BaseModel):
  """Configuration for sampling with optional filters and a sampler."""
  filters: Optional[List[AttributeFilter]] = Field(default_factory=list)
  sampler: WeightedCombinedSampler