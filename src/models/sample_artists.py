from src.models.DataLoader import ArtistHandler
from src.models.Sampling import AttributeWeightedSampling, AttributeFilter, CombinedFilter, WeightedCombinedSampler


def sample_artists_test():
  filters = [
    AttributeFilter(attr="organicness", max=0.5),
    AttributeFilter(attr="bouncyness", min=0.5),
    #AttributeFilter(attr="popularity", max=60),
  ]

  combined_filter = CombinedFilter(filters=filters)

  sampler = [
    AttributeWeightedSampling(attr="popularity", higher_is_better=False),
    #AttributeWeightedSampling(attr="bouncyness", higher_is_better=True),
  ]

  pool = ArtistHandler(sp_session=None).get_pool(1403)

  artists = pool.artists
  filtered = combined_filter(artists)
  sampled = WeightedCombinedSampler(samplers=sampler, n_samples=20)(filtered)

  print([s.name for s in filtered])
  print(set([s.name for s in sampled]))



sample_artists_test()