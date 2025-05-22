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
    this.attr_types = ["bouncyness", "organicness", "popularity"]

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
    artistSamplerSelection.className = 'artist-sampler-section';
    card.appendChild(artistSamplerSelection);
    this.initArtistSamplers(artistSamplerSelection);

    const songSamplerSection = document.createElement('div');
    songSamplerSection.className = 'song-sampler-section';
    card.appendChild(songSamplerSection);
    this.initSongSamplers(songSamplerSection);

    this.container.appendChild(card);
    return card;
  }

  initArtistSamplers(container) {
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
      detailPanel.style.gridTemplateColumns = 'auto 2fr';
      detailPanel.style.gap = '2px 4px';
      detailPanel.style.alignItems = 'left';
      detailPanel.style.padding = '10px';

      // Min input
      const minLabel = document.createElement('label');
      minLabel.textContent = 'Min:';
      const minInput = document.createElement('input');
      minInput.type = 'number';
      minInput.className = 'min-value';
      minInput.value = '0';
      minInput.min = "0";
      minInput.max = attr === "popularity" ? '100' : '1';
      minInput.step = attr === "popularity" ? '1' : '0.001';

      detailPanel.appendChild(minLabel);
      detailPanel.appendChild(minInput);

      // Max input
      const maxLabel = document.createElement('label');
      maxLabel.textContent = 'Max:';
      const maxInput = document.createElement('input');
      maxInput.type = 'number';
      maxInput.className = 'max-value';
      maxInput.value = attr === "popularity" ? '100' : '1';
      maxInput.min = "0";
      maxInput.max = attr === "popularity" ? '100' : '1';
      maxInput.step = attr === "popularity" ? '1' : '0.001';

      detailPanel.appendChild(maxLabel);
      detailPanel.appendChild(maxInput);

      const select = document.createElement("select");
      select.className = "sampling-mode";

      // Prefer higher values
      const preferLabel = document.createElement('label');
      preferLabel.textContent = 'Prefer higher:';
      const preferCheckbox = document.createElement('input');
      preferCheckbox.type = 'checkbox';
      preferCheckbox.className = 'higher-is-better';

      detailPanel.appendChild(preferLabel);
      detailPanel.appendChild(preferCheckbox);

      // MODE
      ["rank", "softmax", "log"].forEach((mode) => {
        const option = document.createElement("option");
        option.value = mode;
        option.textContent = mode;
        select.appendChild(option);
      });
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

      alphaWrapper.appendChild(alphaLabel);
      alphaWrapper.appendChild(alphaInput);
      detailPanel.appendChild(alphaWrapper);

      wrapper.querySelector('.enable-strategy').addEventListener('change', (e) => {
        detailPanel.style.display = e.target.checked ? 'grid' : 'none';
      });
      wrapper.appendChild(detailPanel);

      container.appendChild(wrapper);
    })

    const submitBtn = document.createElement('button');
    submitBtn.innerText = "sample artists";
    submitBtn.onclick = () => this.sendArtistSamplerConfig(container);
    container.appendChild(submitBtn);
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
      const higher_is_better = wrapper.querySelector('.higher-is-better').value;

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

    const payload = {
      sampler: samplerPayload,
      filter: filterPayload
    };

    this.session.updateOnServer(payload, `/api/sample/artists/${this.genre.id}`);
  }

  initSongSamplers(container) {
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

    const submitBtn = document.createElement('button');
    submitBtn.innerText = "sample songs";
    submitBtn.onclick = () => this.sendSongSamplerConfig(container);
    container.appendChild(submitBtn);
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
    console.log("strategies", strategies);
    const payload = {
      genre: this.genre.id,
      sampler: { type: "combined", strategies }
    };

    this.session.updateOnServer(payload, `/api/sample/tracks/${this.genre.id}`);
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
    console.log(this.card, this.container.contains(this.card));
    if (this.card && this.container.contains(this.card)) {
      const card = document.getElementById(this.key);
      if (card) card.remove();
      this.card = null;
    }
  }
}