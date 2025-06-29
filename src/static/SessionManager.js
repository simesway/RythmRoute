class SessionModel {
  constructor(data) {
    this.genre_data = data.genre_data ?? null;
    this.graph = data.graph ?? null;
    this.artists = data.artists ?? null;
    this.factory = data.factory ?? null;
    this.user = data.user ?? null;
  }
}

class SessionManager {
  constructor() {
    this.observers = [];
    this.state = null;
  }

  subscribe(callback) {
    console.log("subscribing", callback)
    this.observers.push(callback);
    if (this.state) callback(this.state); // optional: trigger with current state
  }

  notify() {
    console.log("notifying")
    for (let fn of this.observers) fn(this.state);
  }

  updateFromServer(data) {
    this.state = new SessionModel(data);
    this.notify();
  }

  fetchState() {
    fetch('/api/graph/current_state')
      .then(res => res.json())
      .then(data => this.updateFromServer(data))
      .catch(err => console.error('Session fetch failed:', err));
  }

  updateOnServer(partialUpdate, route) {
    return fetch(route, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(partialUpdate)
    })
      .then(res => res.json())
      .then(data => {
        this.updateFromServer(data);
        return data; // allow further chaining
      })
      .catch(err => {
        console.error('Session update failed:', err);
        throw err; // propagate error
      });
  }
}

// Shared singleton
const session = new SessionManager();
