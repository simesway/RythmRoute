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
      <button onclick="genre_manager.toggleSelectGenre('${this.genre.id}')">Remove</button>
    `;
    card.appendChild(this.attribute_selector())
    card.appendChild(this.toggle_button('toggle-button', "higher_is_better", 'lower_is_better'))
    card.appendChild(this.create_exp_slider(0.01, 100))
    card.appendChild(this.sample_button())
    const artistSamplerSelection = document.createElement('div');
    artistSamplerSelection.className = 'song-sampler-section';
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
      wrapper.className = 'attribute-wrapper';
      wrapper.innerHTML = `
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


      // Alpha slider
      const alphaLabel = document.createElement('label');
      alphaLabel.textContent = 'Alpha:';
      const alphaInput = document.createElement('input');
      alphaInput.type = 'range';
      alphaInput.min = "0";
      alphaInput.max = '100';
      alphaInput.step = '0.01'
      alphaInput.value = '0.5';
      alphaInput.className = 'alpha-slider';

      detailPanel.appendChild(alphaLabel);
      detailPanel.appendChild(alphaInput);

      // Prefer higher values
      const preferLabel = document.createElement('label');
      preferLabel.textContent = 'Prefer higher:';
      const preferCheckbox = document.createElement('input');
      preferCheckbox.type = 'checkbox';
      preferCheckbox.className = 'prefer-higher';

      detailPanel.appendChild(preferLabel);
      detailPanel.appendChild(preferCheckbox);

      wrapper.querySelector('.enable-strategy').addEventListener('change', (e) => {
        detailPanel.style.display = e.target.checked ? 'grid' : 'none';
      });
      wrapper.appendChild(detailPanel);

      container.appendChild(wrapper);
    })
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
            Target date: <input type="date" class="target-date" /><br>
            Sigma days: <input type="number" class="sigma-days" min="0" max="100"/><br>
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
    submitBtn.onclick = () => this.saveSamplerConfig(container);
    container.appendChild(submitBtn);
  }

  saveSamplerConfig(container) {
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

      strategies.push({ strategy: config, weight });
    });
    console.log("strategies", strategies);
    const payload = {
      genre: this.genre.id,
      sampler: { type: "combined", strategies }
    };

    this.session.updateOnServer(payload, `/api/songs/sample/${this.genre.id}`);
  }



  attribute_selector() {
    const selector = document.createElement('select');
    selector.className = 'attr-selector'; // Add class for later selection
    this.attr_types.forEach(type => {
      const option = document.createElement('option');
      option.value = type;
      option.innerText = type;
      if (this.filters.includes(type)) option.selected = true;
      selector.appendChild(option);
    });
    return selector;
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

  create_exp_slider(minExp, maxExp) {
    const container = document.createElement('div');

    const valueDisplay = document.createElement('span');
    valueDisplay.style.marginLeft = '10px';

    const slider = document.createElement('input');
    slider.className = "exp-slider";
    slider.type = 'range';
    slider.min = 0;
    slider.max = 100;
    slider.step = 1;

    const expMap = x => Math.pow(10, (x / 100) * Math.log10(maxExp / minExp) + Math.log10(minExp));

    const update = () => {
      const expValue = expMap(Number(slider.value));
      valueDisplay.innerText = expValue.toFixed(4);
      slider.valueAsExp = expValue;
    };

    slider.oninput = update;
    update();

    container.appendChild(slider);
    container.appendChild(valueDisplay);

    return container;
  }

  sample_button() {
    const button = document.createElement('button');
    button.innerText = 'Sample';
    button.onclick = () => {
      const card = document.getElementById(this.key);
      const selector = card.querySelector('.attr-selector');
      const attr = selector.value;
      const state = card.querySelector('.toggle-button');
      const alpha = card.querySelector('.exp-slider');

      this.session.updateOnServer(
        {attr: attr, higher_is_better: state.value, alpha: alpha.valueAsExp},
        `/api/artists/sample/${this.genre.id}`
      );
    };
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