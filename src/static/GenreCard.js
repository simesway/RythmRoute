class Filter {
  constructor(attribute = '', min = '', max = '') {
    this.attribute = attribute;
    this.min = min;
    this.max = max;
  }

  matches(obj) {
    const val = obj[this.attribute];
    return val >= this.min && val <= this.max;
  }

  toJSON() {
    return {
      attribute: this.attribute,
      min: this.min,
      max: this.max
    };
  }
}


class GenreCard {
  constructor(session, genre, element_id) {
    this.session = session;

    this.key = `genre:${genre.id}`
    this.genre = genre;

    this.filters = [];

    this.container = document.getElementById(element_id);
    this.card = this.initial_card()
    this.container.appendChild(this.card);
  }

  initial_card(){
    const card = document.createElement('div');
    card.className = 'card';
    card.id = this.key;
    card.innerHTML = `
      <h3>${this.genre.name}</h3>
    `;

    const artistSamplerSelection = document.createElement('div');
    artistSamplerSelection.style.border = '1px solid #ccc';
    artistSamplerSelection.style.padding = "8px";
    artistSamplerSelection.className = 'artist-sampler-section';
    card.appendChild(artistSamplerSelection);
    this.initArtistSamplers(artistSamplerSelection);

    const songSamplerSection = document.createElement('div');
    songSamplerSection.style.border = '1px solid #ccc';
    songSamplerSection.style.padding = "8px";
    songSamplerSection.className = 'song-sampler-section';
    card.appendChild(songSamplerSection);
    this.initSongSamplers(songSamplerSection);

    this.container.appendChild(card);
    return card;
  }

  initArtistSamplers(container) {
    const submitBtn = document.createElement('button');
    submitBtn.style.width = "70%"
    submitBtn.style.padding = "2px"
    submitBtn.innerText = "sample artists";
    submitBtn.onclick = () => this.sendArtistSamplerConfig(container);
    container.appendChild(submitBtn);

    const lInput = document.createElement('input');
    lInput.type = 'number';
    lInput.className = 'artist-limit';
    lInput.value = '0';
    lInput.min = "0";
    lInput.style.padding = "0px"
    lInput.style.margin = "2px"
    lInput.style.width = '20%';
    lInput.style.minWidth = '0';
    container.appendChild(lInput);

    const attributes = ["bouncyness", "organicness", "popularity"];

    attributes.forEach(attr => {
      const wrapper = document.createElement('div');
      wrapper.className = 'strategy';


      wrapper.innerHTML += `
        <label><input type="checkbox" class="enable-strategy" /> ${attr}</label>
        <input type="number" class="weight" placeholder="Weight" step="0.1" min="0" max="1" value="0.333"/>
      `;

      const detailPanel = document.createElement('div');
      detailPanel.className = 'details';
      detailPanel.style.display = 'none';
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
      minInput.value = '0';
      minInput.min = "0";
      minInput.max = attr === "popularity" ? '100' : '1';
      minInput.step = attr === "popularity" ? '1' : '0.001';
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
      maxInput.value = attr === "popularity" ? '100' : '1';
      maxInput.min = "0";
      maxInput.max = attr === "popularity" ? '100' : '1';
      maxInput.step = attr === "popularity" ? '1' : '0.001';
      maxInput.style.width = '4em';
      maxInput.style.minWidth = '0';
      maxInput.style.alignSelf = 'end';

      detailPanel.appendChild(maxLabel);
      detailPanel.appendChild(maxInput);

      // higher is better
      const toggleBtn = document.createElement("button");
      let mode = "minimize";
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
      detailPanel.appendChild(modeLabel);
      detailPanel.appendChild(select);


      // Alpha slider
      const alphaWrapper = document.createElement('div');
      alphaWrapper.style.display = 'block';

      const alphaLabel = document.createElement('label');
      alphaLabel.textContent = 'Strength:';
      const alphaInput = document.createElement('input');
      alphaInput.type = 'range';
      alphaInput.min = "0";
      alphaInput.max = '100';
      alphaInput.step = '0.01';
      alphaInput.value = '0.5';
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

    const samplerPayload = {
      type: "WeightedCombinedSampler",
      samplers: samplers,
      weights: weights
    };

    const filterPayload = {
      type: "CombinedFilter",
      filters: filters
    };


    const limit = container.querySelector('.artist-limit').value;

    const payload = {
      limit: limit,
      sampler: samplerPayload,
      filter: filterPayload
    };

    this.session.updateOnServer(payload, `/api/sample/artists/${this.genre.id}`);
    let factory = this.session.state.factory;
    console.log(factory)
  }

  initSongSamplers(container) {
    const submitBtn = document.createElement('button');
    submitBtn.style.width = "70%"
    submitBtn.style.padding = "2px"
    submitBtn.innerText = "sample songs";
    submitBtn.onclick = () => this.sendSongSamplerConfig(container);
    container.appendChild(submitBtn);

    const lInput = document.createElement('input');
    lInput.type = 'number';
    lInput.className = 'track-limit';
    lInput.value = '0';
    lInput.min = "0";
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
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.className = 'core-only';
          checkbox.checked = true;
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
      const wrapper = document.createElement('div');
      wrapper.className = 'strategy';
      wrapper.dataset.type = s.type;

      wrapper.innerHTML = `
        <label><input type="checkbox" class="enable-strategy" /> ${s.label}</label>
        <input type="number" class="weight" placeholder="Weight" step="0.1" min="0" max="1" value="0.25"/>
      `;

      const detailPanel = document.createElement('div');
      detailPanel.className = 'details';
      detailPanel.style.display = 'none';

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
      limit: limit,
      genre: this.genre.id,
      sampler: { type: "combined", strategies }
    };

    this.session.updateOnServer(payload, `/api/sample/tracks/${this.genre.id}`);
    this.render_sampled_tracks()
  }

  render_sampled_tracks() {
    const genre = this.session.state.factory.genres[this.genre.id]
    const tracks = genre.tracks.sampled;

    let sampled_panel = document.getElementById(`${this.genre.id}-sampled-tracks`);
    sampled_panel.innerHTML = "";

    tracks.sort((a, b) => a.name.localeCompare(b.name));
    for (let track of tracks) {
      const el = document.createElement("div");
      el.textContent = track.name;
      sampled_panel.appendChild(el);
    }
  }

  toggle_button(class_name, true_val, false_val) {
    const button = document.createElement('button');
    button.className = class_name;
    let state = false;

    const update = () => {
      button.innerText = state ? true_val : false_val;
      button.value = state;
    };

    button.onclick = () => {
      state = !state;
      update();
    };

    update();
    return button;
  }

  destroy() {
    if (this.card && this.container.contains(this.card)) {
      const card = document.getElementById(this.key);
      if (card) card.remove();
      this.card = null;
    }
  }
}