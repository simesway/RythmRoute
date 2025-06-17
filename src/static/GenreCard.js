class GenreCard {
  constructor(session, genre, element_id) {
    this.session = session;

    this.key = `genre:${genre.id}`
    this.genre = genre;

    this.filters = [];

    this.container = document.getElementById(element_id);
    this.card = this.update_card()

    this.session.subscribe((state) => {
      this.render_sampled_tracks(state);
    });
  }

  update_card(data) {
    if (data) {
      this.genre = data.factory.genres[this.genre.id];
    }

    const template = document.getElementById("genre-card-template");
    const card = template.content.cloneNode(true).children[0];
    card.id = this.key;
    card.querySelector(".genre-name").innerText = this.genre.name;

    // --- Collapse logic ---
    const header = card.querySelector(".genre-name");
    const content = card.querySelector(".card-content");
    header.style.cursor = "pointer";
    header.addEventListener("click", () => {
      content.style.display = content.style.display === "none" ? "block" : "none";
    });
    // -----------------------

    const artistSamplerSection = card.querySelector(".artist-sampler-section");
    this.initArtistSamplers(artistSamplerSection);
    const artistList = card.querySelector('.sampled-artists');
    artistList.id = `${this.genre.id}-sampled-artists`

    const songSamplerSection = card.querySelector(".song-sampler-section");
    this.initSongSamplers(songSamplerSection);

    this.container.appendChild(card);
    return card;
  }

  createAttributeStrategy(
    {
      name,
      weight=0.1,
      min = 0,
      max = 1,
      mode = "rank",
      alpha = 10,
      checked = true,
      higher_is_better = "minimize",
    } = {}) {
    const tmpl = document.getElementById("attribute-strategy-template");
    const node = tmpl.content.cloneNode(true);

    const cb = node.querySelector(".enable-strategy");
    const details = node.querySelector(".strategy-details")
    cb.checked = checked;
    details.style.display = checked ? 'grid' : 'none';
    cb.addEventListener('change', (e) => { details.style.display = e.target.checked ? 'grid' : 'none'; });

    const toggleBtn = node.querySelector(".higher-is-better");
    toggleBtn.value = higher_is_better;
    toggleBtn.textContent = higher_is_better;
    toggleBtn.addEventListener("click", () => {
      let mode = toggleBtn.value;
      mode = mode === "minimize" ? "maximize" : "minimize";
      toggleBtn.textContent = mode;
      toggleBtn.value = mode;
    });

    node.querySelector(".strategy-name").textContent = name;
    node.querySelector(".weight").value = weight;
    node.querySelector(".min-value").value = min;
    node.querySelector(".max-value").value = max;
    node.querySelector(".sampling-mode").value = mode;

    const logMin = Math.log10(0.01);
    const logMax = Math.log10(100);
    const sliderValue = ((Math.log10(alpha) - logMin) / (logMax - logMin)) * 100;
    node.querySelector(".alpha-slider").value = sliderValue;
    return node;
  }

  initArtistSamplers(container) {
    const genreState = this.session.state.factory.genres[this.genre.id];

    const savedConfig = genreState.artists ? genreState.artists : null;
    const savedFilter = savedConfig ? savedConfig.filters : null;
    const savedSampler = savedConfig ? savedConfig.sampler : null;

    let btn = container.querySelector(".sample-btn");
    btn.onclick = () => this.sendArtistSamplerConfig(container);

    let lInput = container.querySelector(".num-samples");
    lInput.value = savedSampler ? savedSampler.n_samples : '1';

    const attributes = ["bouncyness", "organicness", "popularity"];

    const strategies = container.querySelector(".strategies");

    attributes.forEach(attr => {
      const filter = savedFilter ? savedFilter.find(filter => filter.attr === attr) : null;
      const index = savedSampler ? savedSampler.samplers.findIndex(sampler => sampler.attr === attr) : -1;
      const sampler = index !== -1 ? savedSampler.samplers[index] : null;
      const isChecked = filter || sampler;

      const config = {
        name: attr,
        checked: !!isChecked,
        weight: index !== -1 ? savedSampler.weights[index] : "0.1",
        min: filter ? filter.min : "0",
        max: filter ? filter.max : "1",
        mode: sampler ? sampler.mode : "rank",
        alpha: sampler ? sampler.alpha : 1.0,
        higher_is_better:  sampler ? (sampler.higher_is_better ? "maximize":"minimize") : "minimize"
      };

      const strategy = this.createAttributeStrategy(config);
      strategies.appendChild(strategy);
    })
  }

  sendArtistSamplerConfig(container) {
    const wrappers = container.querySelectorAll('.strategy');

    const samplers = [];
    const weights = [];
    const filters = [];

    wrappers.forEach(wrapper => {
      const enabled = wrapper.querySelector('.enable-strategy').checked;
      if (!enabled) return;

      const attr = wrapper.textContent.trim().split('\n')[0].trim();
      const weight = parseFloat(wrapper.querySelector('.weight').value);
      weights.push(weight);

      const min = parseFloat(wrapper.querySelector('.min-value').value);
      const max = parseFloat(wrapper.querySelector('.max-value').value);
      const mode = wrapper.querySelector('.sampling-mode').value;
      const alphaSlider = wrapper.querySelector('.alpha-slider');
      const alpha = Math.pow(10, (alphaSlider.value / 100) * Math.log10(100 / 0.01) + Math.log10(0.01));
      const higher_is_better = wrapper.querySelector('.higher-is-better').value === "maximize";

      samplers.push({
        type: "AttributeWeightedSampling",
        attr: attr,
        higher_is_better: higher_is_better,
        alpha: alpha,
        mode: mode
      });

      filters.push({
        type: "AttributeFilter",
        attr: attr,
        min: min,
        max: max
      });
    });

    const limit = container.querySelector('.num-samples').value;

    const samplerPayload = {
      type: "WeightedCombinedSampler",
      samplers: samplers,
      weights: weights,
      n_samples: limit
    };

    const payload = {
      sampler: samplerPayload,
      filters: filters
    };

    const btn = container.querySelector(".sample-btn");
    btn.innerText = "loading..."

    this.session.updateOnServer(payload, `/api/sample/artists/${this.genre.id}`)
    .then(() => {
      btn.innerText = "sample artists";
    })
    .catch((error) => {
      btn.innerText = "sample artists";
      console.error("Update failed:", error);
      // optionally show error to user
    });
  }

  initSongSamplers(container) {
    const genreState = this.session.state.factory.genres[this.genre.id];

    const savedConfig = genreState.tracks ? genreState.tracks : null;
    const savedSampler = savedConfig ? savedConfig.sampler : null;
    const savedStrats = savedSampler && savedSampler.strategies.length > 0 ? savedSampler.strategies : null;

    const submitBtn = container.querySelector(".sample-btn");
    submitBtn.onclick = () => this.sendSongSamplerConfig(container);

    const lInput = container.querySelector(".num-samples");
    lInput.value = savedSampler ? savedSampler.n_samples : '1';

    const strats = container.querySelector(".strategies");
    const tmpl = document.getElementById("song-sampler-template");
    const node = tmpl.content.cloneNode(true);
    strats.appendChild(node);

    container.querySelectorAll(".strategy").forEach(strategy => {
      const type = strategy.dataset.type;
      const strategyConfig = savedStrats.find(s => s.strategy.type === type) || null;
      console.log(type, strategyConfig)

      const enable = strategy.querySelector('.enable-strategy');
      const weight = strategy.querySelector('.weight');
      const details = strategy.querySelector('.strategy-details');

      if (strategyConfig) {
        enable.checked = true;
        weight.value = strategyConfig.weight;
        details.style.display = 'block';
      }

      enable.addEventListener('change', e => {
        details.style.display = e.target.checked ? 'block' : 'none';
      });

      if (type === "album_cluster" && strategyConfig) {
        strategy.querySelector('.core-only').checked = strategyConfig.strategy.core_only;
        const excludes = strategyConfig.strategy.exclude_types || [];
        strategy.querySelectorAll('.type-grid input').forEach(cb => {
          cb.checked = excludes.includes(cb.value);
        });
      }

      if (type === "nearest_release_date" && strategyConfig) {
        strategy.querySelector('.target-date').value = strategyConfig.strategy.target_date || "";
        strategy.querySelector('.sigma-days').value = strategyConfig.strategy.sigma_days || 180;
        strategy.querySelector('.core-only').checked = strategyConfig.strategy.core_only;
      }
    });

    container.querySelector('.sampled-tracks').id = `${this.genre.id}-sampled-tracks`;
  }

  sendSongSamplerConfig(container) {
    const strategies = [];

    container.querySelectorAll('.strategy').forEach(s => {
      const enabled = s.querySelector('.enable-strategy').checked;
      if (!enabled) return;

      const type = s.dataset.type;
      const weight = parseFloat(s.querySelector('.weight').value || "0");
      const config = { type };

      if (type === "nearest_release_date") {
        config.target_date = s.querySelector('.target-date').value;
        config.sigma_days = parseFloat(s.querySelector('.sigma-days').value);
        config.core_only = s.querySelector('.core-only').checked;
      }

      if (type === "album_cluster") {
        config.core_only = s.querySelector('.core-only').checked;

        const excludeTypes = [];
        s.querySelectorAll('input[type="checkbox"]').forEach(cb => {
          if (
            cb.className !== 'core-only' &&
            cb.checked &&
            cb.value &&
            cb.value !== 'on'
          ) {
            excludeTypes.push(cb.value);
          }
        });
        config.exclude_types = excludeTypes;
      }

      strategies.push({ strategy: config, weight: weight });
    });

    const limit = container.querySelector(".num-samples").value;

    const payload = {
      genre: this.genre.id,
      sampler: { type: "combined", strategies: strategies, n_samples: limit}
    };

    const btn = container.querySelector(".sample-btn");
    btn.innerText = "loading...";

    this.session.updateOnServer(payload, `/api/sample/tracks/${this.genre.id}`)
    .then(() => {
      btn.innerText = "sample tracks";
    })
    .catch((error) => {
      btn.innerText = "sample tracks";
      console.error("Update failed:", error);
    });
  }


  render_sampled_tracks() {
    const genre = this.session.state.factory.genres[this.genre.id]

    if (!genre.tracks) return;
    const tracks = genre.tracks.sampled;

    if (!tracks) return;
    let sampled_panel = document.getElementById(`${this.genre.id}-sampled-tracks`);
    sampled_panel.innerHTML = "";

    tracks.sort((a, b) => a.name.localeCompare(b.name));
    for (let track of tracks) {
      const el = document.createElement("div");
      el.textContent = track.name;
      sampled_panel.appendChild(el);
    }
  }

  destroy() {
    if (this.card && this.container.contains(this.card)) {
      const card = document.getElementById(this.key);
      if (card) card.remove();
      this.card = null;
    }
  }
}