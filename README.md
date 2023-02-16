# Backend Data Scraper for Babiri

This is an implementation of the backend to [Babiri](https://github.com/sreilly64/babiri_v1), a Pokémon stats aggregation and visualization website for competitive VGC and OU players.

## About

The main script, ShowdownDataScraper.py, is designed to be run once per day to scrape Pokémon Showdown's public ladder API for a specific format. It then saves 100 of the top publicly available teams, as well as usage data (not yet implemented), to a MongoDB database.

Also included is a bonus script, SpriteDownloader.py, that will download any missing Pokémon sprites from Showdown to the specified folder if needed for the frontend.

## Getting Started
### Prerequisites
- A version of [Python 3](https://www.python.org/downloads/) to run the script
- Access to a MongoDB database with the following 2 collections: 'teams' and 'usage'. 
    - You can either sign up for a [free cloud database](https://www.mongodb.com/cloud/atlas/register) or [download and host one yourself](https://www.mongodb.com/try/download/community).

To run the program, first set the 'mongoURI', 'databaseName', and 'format' fields in your environment variables to your MongoDB connection URI and database name as well as the desired Showdown format. Then simply run the main script ShowdownDataScraper.py.


## Acknowledgements

- [Pokémon Showdown](https://pokemonshowdown.com/)
- [Pikalytics](https://pikalytics.com/)

