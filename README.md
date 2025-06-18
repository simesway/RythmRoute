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
git clone 
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

4. **Modify the .env file**
- Copy the template `src/.env.template` file.
- Fill the missing environment variables.

5. **Set up the database**
- Provide a valid PostgreSQL connection string in the `.env`-file (SQLAlchemy uses this to connect).
- A compact SQL dump file `data.sql` is included to initialize the database with pre-scraped data.
- Import the dump into your PostgreSQL database:
```bash
psql -U <user> -d <dbname> -f data.sql
```
- Optionally execute the Scraping scripts directly.

6. **Start the server**
```bash
uvicorn server:app --reload
```

7. **Access the app**
```url
http://127.0.0.1:8000
```



