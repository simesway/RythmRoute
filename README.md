# RythmRoute

**RythmRoute** is a web application that helps users discover new music by transparently and interactively creating Spotify playlists. Unlike Spotify's black-box recommendations, RythmRoute allows users to explore genre relationships, sample artists and songs using customizable strategies, and build or update playlist based on their preferences.

Users can:
- Select music genres and explore related subgenres, fusion genres, or influenced genres.
- Sample artists within genres using filters and weighted sampling strategies.
- Sample songs from selected artists using various methods.
- Repeat sampling steps as often as desired to fine-tune the playlist configuration.
- Create or update Spotify playlists based on the sampling results.

The goal is to provide transparency and control over the playlist creation process, enabling users to discover artists, genres, and tracks that match their interests.

## Features

- **Genre graph navigation:** Navigate through a graph of ~7500 genres and 2500 relationships (subgenres, fusion genres, influenced-by links).
- **Artist sampling:** Filter and weight artist selection within chosen genres.
- **Song sampling:** Use customizable strategies (e.g. top songs, random release, cluster by album type, nearest release date).
- **Playlist creation and updating:** Build or modify Spotify playlists directly from the app.
- **Resampling:** Sampling steps can be repeated any number of times.
- **Graph visualizations:** 
  - Genre relationships (using NetworkX and p5.js layouts).
  - Artist pools plotted on axes representing attributes (X: atmosphericness/bouncyness, Y: organicness/electricness).
- **Frontend:** Highly reactive interface using p5.js and plain JavaScript without reloads.
- **Backend:** Consistent API powering the frontend via FastAPI.

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, Redis, NetworkX, Spotipy
- **Frontend:** p5.js, Vanilla JavaScript, HTML, CSS
- **Other tools:** BeautifulSoup (used privately for database generation, not part of the deliverable)

## Setup & Installation

1. **Clone the repository**
```bash
git clone https://github.com/simesway/RythmRoute.git
cd RythmRoute
```

2. **Create a virtual environment**
```
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database-Setup**

- Create an empty PostgreSQL database.
- Initialize custom types and tables:
```bash
python src/scripts/db-init.py
```
- Import the data:
```bash
psql -U <user> -d <dbname> -f data.sql
```

5. **Modify the .env file**
- Copy the template `src/.env.template` file.
```bash
cp src/.env.template src/.env
```
- Fill the missing environment variables:
  - **PostgreSQL**: username, password, host, port, name
  - **Redis**: host, port
  - **Spotify**: client-id, client-secret
    1. sign in to Spotify on [developer.spotify.com](https://developer.spotify.com)
    2. go to the API Dashboard and "Create app"
    3. add `http://localhost:8000/spotify/callback` to the list of "Redirect URIs"
    4. check Web API under "APIs used"
    5. Save settings
    6. add Client ID and Client Secret to the `.env`

6. **Start the server**
```bash
uvicorn server:app --reload --port 8000
```

7. **Access the app**
```url
http://127.0.0.1:8000
```

## Database

RythmRoute uses **PostgreSQL** to store music data scraped from [everynoise.com](https://everynoise.com) and [musicbrainz.org](https://musicbrainz.org).

### Tables
- **Genre** represents a music genre with its name and additional data.
- **Artist** Represents an artist with metadata such as name, Spotify ID, popularity, follower count, and Spotify genre tags.
- **Genre Relationship** Models how genres relate to each other (`SUBGENRE_OF`, `INFLUENCED_BY`, `FUSION_OF`). This enables traversal through the genre graph for discovery and visualization.
- **Artist-Genre Links** Connects artists to genres with additional attributes that position the artist within its genres.

### Attributes
- **Organic Value**: lower values indicate more organic (natural, acoustic) music; higher values more mechanical or electric.
- **Bouncy Value**: Lower values indicate denser, more atmospheric music; higher values spikier, more bouncy.

## Planned Features
- Advanced playlist sorting strategies (e.g. order tracks from bouncy to atmospheric).
- Load and modify existing Spotify playlists.
- Automatically regenerate playlist periodically (useful on a remote server).
- Expand genre relationships (currently ~3200 on ~7500 genres).
- Country and regional data for advanced exploration.

## Known limitations
- The genre graph is incomplete (missing genre relationships).
- Not optimized for deployment on a remote server (most time/computational expensive features are in sync).- Server responses on user input are not optimized (Current State is being fully recomputed and sent).
- Server responses on user input are not optimized (current state is fully recomputed and sent).
- Error handling is incomplete and not all errors are adequately managed.
- The UI is not yet fully intuitive or self-explanatory.