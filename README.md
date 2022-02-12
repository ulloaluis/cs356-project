# CS 356 Project (Winter 2022)

Course Project for the CS 356 class in the Winter 2022 quarter, by Tim
Chirananthavat and Luis Ulloa.

This project manages dependencies using
[Pipenv](https://pipenv.pypa.io/en/latest/) in order to ensure consistent
results when running on different machines. (No need to use virtualenv, which is
redundant.)

To initialize dependencies on a new machine, run `pipenv sync`.

To run a file in this project, use `pipenv run python something.py`.
Alternatively, run `pipenv shell` at the start of your session, and then you can
run `python something.py` as normal.