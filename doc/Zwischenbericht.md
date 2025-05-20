# Zwischenbericht (DAPI)
Ausgewählte Projekte der Informatik

Sommersemester 2025

## Projektname
**RythmRoute**

## Mitarbeitende
Simon Eiber

## Feature Liste
Das Projekt befindet sich gerade in der Ausarbeitung der UI, da auf der Seite des Backends bereits die Funktionalität zur Erstellung einer Playlist realisiert wurde:
- Spotify Authentification und Playlist Erstellung
- effizientes Caching von Spotify Daten -> schnelle wiederholte Datenabfrage
- Verschiedenste Strategien zum sampling von Artists und Songs
- Zentrale Klasse `PlaylistFactory` führt die Playlist-Konfiguration des Benutzers aus
- grobe UI Struktur mit dem Genre-Graphen, Sampling und Visualisierung von Artists und Erstellen einer Playlist

### Datenbank

| Bezeichnung                                                | geschätzter Aufwand | benötigter Aufwand |
|------------------------------------------------------------|---------------------|--------------------|
| Hinzufügen von nicht existierenden Genre-Genre-Beziehungen | 10                  | 0                  |
| Datenaufbereitung (Normalisierung, etc)                    | 5                   | 2                  |
| total                                                      | 15                  | 2                  |

### Playlist Generierung

| Bezeichnung                                           | geschätzter Aufwand | benötigter Aufwand |
|-------------------------------------------------------|---------------------|--------------------|
| Erstellung eines zentralen Genre Graphen              | 15                  | 10                 | 
| Artist-Sampling Logik (Filtern, Sampling Algorithmen) | 15                  | 10                 | 
| Song-Sampling Logik                                   | 15                  | 20                 | 
| (Spotify-)Playlist-Generierungs Logik                 | 10                  | 12                 | 
| Laufzeit und Speicheroptimierung (Caching, etc)       | 25                  | 30                 | 
| total                                                 | 80                  | 82                 | 


### Visualisierung

| Bezeichnung                                                  | geschätzter Aufwand | benötigter Aufwand |
|--------------------------------------------------------------|---------------------|--------------------|
| Web-Hosting und User/Session Handling                        | 20                  | 10                 | 
| Implementierung eines interaktiven Genre Graphen             | 10                  | 15                 | 
| Visualisierung des Sampling                                  | 5                   | 10                 | 
| UI mit möglichst großer Kontrolle über die Sampling Prozesse | 20                  | 15                 | 
| total                                                        | 55                  | 50                 | 