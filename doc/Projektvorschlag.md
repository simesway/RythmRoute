# Projektvorschlag (DAPI)
Ausgewählte Projekte der Informatik

Sommersemester 2025
## Projektname
**RythmRoute**

## Mitarbeitende
Simon Eiber

## Feature Liste
Dieses Projekt wurde als privates Projekt gestartet und wird von mir im Rahmen des DAPI Projektes weitergeführt.
Zu Beginn des Semester existierte eine Datenbank mit gescrapten Musik Genre, Artist und Relationship Daten.

### Datenbank

| Bezeichnung                                                | geschätzter Aufwand |
|------------------------------------------------------------|---------------------|
| Hinzufügen von nicht existierenden Genre-Genre-Beziehungen | 10                  |
| Datenaufbereitung (Normalisierung, etc)                    | 5                   |
| total                                                      | 15                  | 

### Playlist Generierung

| Bezeichnung                                           | geschätzter Aufwand |
|-------------------------------------------------------|---------------------|
| Erstellung eines zentralen Genre Graphen              | 15                  |
| Artist-Sampling Logik (Filtern, Sampling Algorithmen) | 15                  |
| Song-Sampling Logik                                   | 15                  |
| (Spotify-)Playlist-Generierungs Logik                 | 10                  |
| Laufzeit und Speicheroptimierung (Caching, etc)       | 25                  |
| total                                                 | 80                  |


### Visualisierung

| Bezeichnung                                                           | geschätzter Aufwand |
|-----------------------------------------------------------------------|---------------------|
| Web-Hosting und User/Session Handling                                 | 20                  |
| Implementierung eines interaktiven Genre Graphen                      | 10                  |
| Visualisierung des Artist Sampling                                    | 5                   |
| UI mit möglichst großer Kontrolle über die Sampling Prozesse          | 20                  |
| total                                                                 | 55                  |