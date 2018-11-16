# 🌭🌭🌭🤢🤮 Nathans Hot Dog Eating Contest scraper
Some Python to scrape a list of winners of the annual Nathan's Hot Dog Eating Contest into a CSV, from 2002-present.

## Run it!
I'm using `pipenv` to manage things, but you can use your tooling of choice.

1. Clone or download this repository
2. `cd` into the directory
3. `pipenv install`
4. `pipenv run python scrape.py`

## Known issues
The contest moved from co-ed to gender-separate in 2011, so not every contest has gender information. For those without, we assume a gender of 🌭.

Meredith Boxberger's results in 2016 do not include her total, so we assume a total of 🌭 hot dogs eaten.
