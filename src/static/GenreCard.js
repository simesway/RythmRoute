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
      // Collapse all other card contents
      document.querySelectorAll(".card-content").forEach(el => {
        if (el !== content) el.style.display = "none";
      });

      // Toggle this one
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

    this.session.updateOnServer(payload, `/api/sample/artists/${this.genre.id}`);
  }

  initSongSamplers(container) {
    const genreState = this.session.state.factory.genres[this.genre.id];

    const savedConfig = genreState.tracks ? genreState.tracks : null;
    const savedSampler = savedConfig ? savedConfig.sampler : null;
    const savedStrats = savedSampler && savedSampler.strategies.length > 0 ? savedSampler.strategies : null;

    const submitBtn = document.createElement('button');
    submitBtn.style.width = "70%"
    submitBtn.style.padding = "2px"
    submitBtn.innerText = "sample songs";
    submitBtn.onclick = () => this.sendSongSamplerConfig(container);
    container.appendChild(submitBtn);

    const lInput = document.createElement('input');
    lInput.type = 'number';
    lInput.className = 'track-limit';
    lInput.value = savedSampler ? savedSampler.n_samples : '1';
    lInput.min = "1";
    lInput.style.padding = "0px"
    lInput.style.margin = "2px"
    lInput.style.width = '20%';
    lInput.style.minWidth = '0';
    container.appendChild(lInput);

    const strategies = [
      { type: "top_songs", label: "Top Songs", details: null },
      { type: "random_release", label: "Random Release", details: null },
      {
        type: "album_cluster", label: "Album Cluster", details: (parent) => {
          const strategyConfig = savedStrats ? savedStrats.find(strat => strat.strategy.type === "album_cluster") || null : null;

          const core_only = strategyConfig ? strategyConfig.strategy.core_only : false;
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.className = 'core-only';
          checkbox.checked = strategyConfig ? strategyConfig.strategy.core_only : true;
          console.log(core_only, checkbox.checked)
          parent.appendChild(document.createTextNode("Core only "));
          parent.appendChild(checkbox);

          const grid = document.createElement('div');
          grid.style.display = 'grid';
          grid.style.gridTemplateColumns = 'repeat(2, auto)';
          grid.style.padding = '5px';

          ['album', 'single', 'ep', 'compilation'].forEach((label, i) => {
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.id = `option${i}`;
            cb.value = label;
            cb.checked = strategyConfig ? strategyConfig.strategy.exclude_types.includes(label) : false;

            const cbLabel = document.createElement('label');
            cbLabel.htmlFor = cb.id;
            cbLabel.textContent = label;

            const wrapper = document.createElement('div');
            wrapper.appendChild(cb);
            wrapper.appendChild(cbLabel);

            grid.appendChild(wrapper);
          });
          parent.innerHTML += "<br>";
          parent.appendChild(document.createTextNode("Exclude types:"));
          parent.appendChild(grid);

        }
      },
      {
        type: "nearest_release_date", label: "Nearest Release", details: (parent) => {
          parent.innerHTML = `
            Target date: <input type="text" class="target-date" placeholder="YYYY or YYYY-MM or YYYY-MM-DD" /><br>
            Sigma days: <input type="number" class="sigma-days" min="0" value="180"/><br>
            <label><input type="checkbox" class="core-only" checked /> Core only</label>
          `;
        }
      }
    ];

    strategies.forEach(s => {
      const strategyConfig = savedStrats ? savedStrats.find(strat => strat.strategy.type === s.type) || null : null;

      const wrapper = document.createElement('div');
      wrapper.className = 'strategy';
      wrapper.dataset.type = s.type;

      wrapper.innerHTML = `
        <label><input type="checkbox" class="enable-strategy" ${strategyConfig ? "checked":""}/> ${s.label}</label>
        <input type="number" class="weight" placeholder="Weight" step="0.1" min="0" max="10" value="${strategyConfig ? strategyConfig.weight : "0.1"}"/>
      `;

      const detailPanel = document.createElement('div');
      detailPanel.className = 'details';
      detailPanel.style.display = strategyConfig ? 'block' : 'none';

      if (s.details) s.details(detailPanel);
      wrapper.appendChild(detailPanel);

      wrapper.querySelector('.enable-strategy').addEventListener('change', (e) => {
        detailPanel.style.display = e.target.checked ? 'block' : 'none';
      });

      container.appendChild(wrapper);
    });

    const trackList = document.createElement('div');
    trackList.id = `${this.genre.id}-sampled-tracks`
    trackList.className = 'sampled-artists';
    trackList.style.maxHeight = '8rem';
    trackList.style.overflowY = 'auto';
    trackList.style.border = '1px solid #ccc';
    trackList.style.padding = '8px';

    container.appendChild(trackList);
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

    const limit = container.querySelector(".track-limit").value;

    const payload = {
      genre: this.genre.id,
      sampler: { type: "combined", strategies: strategies, n_samples: limit}
    };

    this.session.updateOnServer(payload, `/api/sample/tracks/${this.genre.id}`);
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