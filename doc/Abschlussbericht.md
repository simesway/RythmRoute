# Abschlussbericht (DAPI)
Ausgewählte Projekte der Informatik

Sommersemester 2025

## Projektname
**RythmRoute**

Github Repository: [https://github.com/simesway/RythmRoute](https://github.com/simesway/RythmRoute)

## Mitarbeitende
Simon Eiber

## Feature Liste

### Datenbank

| Bezeichnung                                                | geschätzter Aufwand | benötigter Aufwand |
|------------------------------------------------------------|---------------------|--------------------|
| Hinzufügen von nicht existierenden Genre-Genre-Beziehungen | 10                  | nicht realisiert   |
| Datenaufbereitung (Normalisierung, etc)                    | 5                   | 2                  |
| total                                                      | 15                  | 2                  |

### Playlist Generierung

| Bezeichnung                                           | geschätzter Aufwand | benötigter Aufwand | 
|-------------------------------------------------------|---------------------|--------------------|
| Erstellung eines zentralen Genre Graphen              | 15                  | 10                 | 
| Artist-Sampling Logik (Filtern, Sampling Algorithmen) | 15                  | 10                 | 
| Song-Sampling Logik                                   | 15                  | 20                 | 
| (Spotify-)Playlist-Generierungs Logik                 | 10                  | 15                 | 
| Laufzeit und Speicheroptimierung (Caching, etc)       | 25                  | 40                 | 
| total                                                 | 80                  | 95                 | 


### Visualisierung

| Bezeichnung                                                  | geschätzter Aufwand | benötigter Aufwand |
|--------------------------------------------------------------|---------------------|--------------------|
| Web-Hosting und User/Session Handling                        | 20                  | 10                 | 
| Implementierung eines interaktiven Genre Graphen             | 10                  | 15                 | 
| Visualisierung des Sampling                                  | 5                   | 20                 | 
| UI mit möglichst großer Kontrolle über die Sampling Prozesse | 20                  | 25                 | 
| total                                                        | 55                  | 70                 | 


## Herausforderungen

| Herausforderung                                                                                             | Lösung                                                                                               |
|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Spotify API Rate Limits                                                                                     | Caching implementiert, um wiederholte Anfragen zu vermeiden und die Reaktivität der App zu verbessern. |
| Konsistenz zwischen Frontend- und Backend-Konfiguration                                                     | Strukturierte Datenmodelle geschaffen und Codebasis überarbeitet, um Konsistenz sicherzustellen.     |
| Komplexe/Dynamische Datenstrukturen (Sampler, Spotify-Objekte, Session Daten, Playlist, User Konfiguration) | Einsatz von Pydantic-Modellen für Validierung und Redis-Kompatibilität                               |  
| Skalierbarkeit und Performance                                                                              | Nutzung von effizienten Bibliotheken (NetworkX, p5.js, numpy)                                        | 
| Benutzerfreundlichkeit und Reaktivität (ohne Reloads und schnell)                                           | Verwendung von Vanilla JS für ein hochreaktives Frontend mit asynchronem API-Zugriffen. | 

