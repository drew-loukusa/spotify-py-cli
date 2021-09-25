## Overview 
This project is comprised of several distinct and loosely coupled items. The distinct items are the CLI app itself, a facade constructed on the `spotipy` Spotify wrapper, and a number of small, interface implementing classes used by the facade.

## CLI App
The CLI app is composed with 1 item, a facade instance. 

## Facade
The facade, `SpotipySpotifyFacade`, is composed with, and responsible for instantiating a `spotipy Spotify` instance. The facade then passes this Spotify instance around where needed.

## Interfaces 



## Concrete Classes

All concrete classes take in as an argument, a Spotify instance from the `spotipy` module. 

Since no data is actually stored locally for ANY `Item` or `ItemCollection` class, they only actually EMULATE a data class. They have no properties, and all actions invoked result in API calls being made. (Some caching may be added in a future update). Because of this, all concrete classes need to be able to make api calls for you, and thus they all need access to a Spotify instance(more accuratley THE Spotify instance). 

I've designed the classes to take responsibilty from the user. The idea is that you don't have to know how to add an episode to a user's saved episodes, you just need to create a `SavedEpisodes` object and call `add(item)` on it. 
the `SavedEpisodes` class knows how to complete that operation. 

Encapsulate what changes.