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
    this.container.appendChild(card);
    return card;
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