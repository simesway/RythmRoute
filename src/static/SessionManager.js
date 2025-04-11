class SessionModel {
  constructor(data) {
    this.graph = data.graph ?? null;
    this.artists = data.artists ?? null;
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
    fetch(route, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(partialUpdate)
    })
      .then(res => res.json())
      .then(data => this.updateFromServer(data))
      .catch(err => console.error('Session update failed:', err));
  }
}

// Shared singleton
const session = new SessionManager();
