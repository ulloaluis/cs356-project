# CS 356 Project (Winter 2022)

Course Project for the CS 356 class in the Winter 2022 quarter, by Tim
Chirananthavat and Luis Ulloa.

## Setup

This project manages dependencies using
[Pipenv](https://pipenv.pypa.io/en/latest/) in order to ensure consistent
results when running on different machines. (No need to use virtualenv, which is
redundant.)

To initialize dependencies on a new machine, run `pipenv sync`.

To run a file in this project, use `pipenv run python something.py`.
Alternatively, run `pipenv shell` at the start of your session, and then you can
run `python something.py` as normal.

## Data source

List of websites used here (file: `tranco_36PL-1m.csv.zip`) is from
[Tranco](https://tranco-list.eu/list/36PL/1000000). ID 36PL,  generated on
11 February 2022