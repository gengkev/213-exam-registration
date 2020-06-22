# Exam Registration System

Designed to allow for 15-213 students to register to take their exams.
Students can select one of multiple exam slots over the course of multiple
days, which consist of one or more time slots.

Installation:

    python3 -m pip install poetry
    poetry install

Running development server:

    poetry shell
    python manage.py runserver

Or just:

    poetry run python manage.py runserver

How to run assorted scripts in production:

    $ ./run_script.sh import_instructors.py

How to update the production server (git pull, etc):

    $ ./update.sh
