# Backend Data Scraper for Babiri

This is an implementation of the backend to [Babiri](https://github.com/sreilly64/babiri_v1), a Pokémon stats aggregation and visualization website for competitive VGC and OU players.

## About

The main script, ShowdownDataScraper.py, is designed to be run once per day to scrape Pokémon Showdown's public ladder API for a specific format and to save the top 100 teams as well as usage data (not yet implemented) to a MongoDB database.

A bonus script is also included, SpriteDownloader.py, that will download any missing Pokémon sprites from Showdown to the specified folder if needed for the frontend.

## Getting Started
### Prerequisites
Besides some version of [Python 3](https://www.python.org/downloads/) to run the script, you will also need access to a MongoDB database with the following 2 collections: 'teams' and 'usage'. You can either sign up for a [free cloud database](https://www.mongodb.com/cloud/atlas/register) or [download and host one yourself](https://www.mongodb.com/try/download/community).

Before running ShowdownDataScraper.py, be sure to set the 'mongoURI', 'databaseName', and 'format' in your environment variables.


## Acknowledgements

- [Pokémon Showdown](https://pokemonshowdown.com/)
- [Pikalytics](https://pikalytics.com/)

