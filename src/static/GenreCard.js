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

    const artistSamplerSection = card.querySelector(".artist-sampler-section");
    this.initArtistSamplers(artistSamplerSection);

    const songSamplerSection = card.querySelector(".song-sampler-section");
    this.initSongSamplers(songSamplerSection);

    this.container.appendChild(card);
    return card;
  }

  initArtistSamplers(container) {
    const genreState = this.session.state.factory.genres[this.genre.id];

    const savedConfig = genreState.artists ? genreState.artists : null;
    const savedFilter = savedConfig ? savedConfig.filters : null;
    const savedSampler = savedConfig ? savedConfig.sampler : null;

    console.log(savedFilter, savedSampler);

    let btn = container.querySelector(".sample-btn");
    btn.onclick = () => this.sendArtistSamplerConfig(container);

    let lInput = container.querySelector(".num-samples");
    lInput.value = savedSampler ? savedSampler.n_samples : '1';

    const attributes = ["bouncyness", "organicness", "popularity"];

    attributes.forEach(attr => {
      const filter = savedFilter ? savedFilter.find(filter => filter.attr === attr) : null;
      const index = savedSampler ? savedSampler.samplers.findIndex(sampler => sampler.attr === attr) : -1;
      const sampler = index !== -1 ? savedSampler.samplers[index] : null;
      const weight = index !== -1 ? savedSampler.weights[index] : "0.333";
      const isChecked = filter || sampler;
      console.log(sampler, weight)

      const wrapper = document.createElement('div');
      wrapper.className = 'strategy';


      wrapper.innerHTML += `
        <label><input type="checkbox" class="enable-strategy" ${isChecked ? "checked":""}/> ${attr}</label>
        <input type="number" class="weight" placeholder="Weight" step="0.1" min="0" max="1" value="${weight}"/>
      `;



      const detailPanel = document.createElement('div');
      detailPanel.className = 'details';
      detailPanel.style.display = isChecked ? 'grid':'none';
      detailPanel.style.gridTemplateColumns =  'repeat(4, max-content)';
      detailPanel.style.gap = '2px 4px';
      detailPanel.style.alignItems = 'left';
      detailPanel.style.padding = '10px';

      // Min input
      const minLabel = document.createElement('label');
      minLabel.textContent = 'min:';
      const minInput = document.createElement('input');
      minInput.type = 'number';
      minInput.className = 'min-value';
      minInput.value = filter ? filter.min : "0";
      minInput.min = "0";
      minInput.max = attr === "popularity" ? '100' : '1';
      minInput.step = attr === "popularity" ? '1' : '0.0025';
      minInput.style.width = '4em';
      minInput.style.minWidth = '0';
      minInput.style.alignSelf = 'end';

      detailPanel.appendChild(minLabel);
      detailPanel.appendChild(minInput);

      // Max input
      const maxLabel = document.createElement('label');
      maxLabel.textContent = 'max:';
      const maxInput = document.createElement('input');
      maxInput.type = 'number';
      maxInput.className = 'max-value';
      maxInput.value = filter ? filter.max : (attr === "popularity" ? '100' : '1');
      maxInput.min = "0";
      maxInput.max = attr === "popularity" ? '100' : '1';
      maxInput.step = attr === "popularity" ? '1' : '0.005';
      maxInput.style.width = '4em';
      maxInput.style.minWidth = '0';
      maxInput.style.alignSelf = 'end';

      detailPanel.appendChild(maxLabel);
      detailPanel.appendChild(maxInput);

      // higher is better
      const toggleBtn = document.createElement("button");
      let mode = sampler ? (sampler.higher_is_better ? "maximize":"minimize") : "minimize";
      toggleBtn.className = "higher-is-better"
      toggleBtn.textContent = mode;

      toggleBtn.addEventListener("click", () => {
        mode = mode === "minimize" ? "maximize" : "minimize";
        toggleBtn.textContent = mode;
        toggleBtn.value = mode;
      });
      toggleBtn.style.gridColumn = 'span 2';
      detailPanel.appendChild(toggleBtn);

      // MODE
      const modeLabel = document.createElement('label');
      modeLabel.textContent = 'mode:';
      const select = document.createElement("select");
      select.className = "sampling-mode";
      ["rank", "softmax", "log"].forEach((mode) => {
        const option = document.createElement("option");
        option.value = mode;
        option.textContent = mode;
        select.appendChild(option);
      });
      select.value = sampler ? sampler.mode : "rank";
      detailPanel.appendChild(modeLabel);
      detailPanel.appendChild(select);


      const logMin = Math.log10(0.01);
      const logMax = Math.log10(100);
      const alpha = sampler ? sampler.alpha : 1.0;
      const sliderValue = ((Math.log10(alpha) - logMin) / (logMax - logMin)) * 100;
      const alphaInput = document.createElement('input');
      alphaInput.type = 'range';
      alphaInput.min = "0";
      alphaInput.max = '100';
      alphaInput.step = '0.01';
      alphaInput.value = sliderValue;
      alphaInput.className = 'alpha-slider';
      alphaInput.style.gridColumn = '1 / -1';
      alphaInput.style.height = 'auto';
      alphaInput.style.minHeight = '0';


      detailPanel.appendChild(alphaInput);

      wrapper.querySelector('.enable-strategy').addEventListener('change', (e) => {
        detailPanel.style.display = e.target.checked ? 'grid' : 'none';
      });
      wrapper.appendChild(detailPanel);

      container.appendChild(wrapper);
    })

    const artistList = document.createElement('div');
    artistList.id = `${this.genre.id}-sampled-artists`
    artistList.className = 'sampled-artists';
    artistList.style.maxHeight = '8rem';
    artistList.style.overflowY = 'auto';
    artistList.style.border = '1px solid #ccc';
    artistList.style.padding = '8px';

    container.appendChild(artistList);
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