Leech
=====

A simple url shorten service based on Django, Redis and SQLite

Prerequisites
-------------
1. Python environment, with **pip** installed
2. Redis

Usage
-----

1. Clone the code:
    $ git clone https://github.com/ritksm/leech.git
    $ cd leech
2. Install required packages:
    $ pip install -r requirements.txt (You may use virtualenv here)
3. Copy local setting file:
    $ cp leech_devel/local_settings.example.py leech_devel/local_settings.py
4. Create and sync database:
    $ python manage.py syncdb
5. Run Django server:
    $ python manage.py runserver
6. Visit http://localhost:8000/

License
-------
This project is using the MIT License. See LICENSE file for detail.

Author
------
Jack River (ritksm@gmail.com)

Contribute
----------
You can fork this repo and send me pull requests. I would appreciate that.