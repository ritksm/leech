Leech
=====

A simple url shorten service based on Django, Redis and SQLite


Prerequisites
-------------
1. Python environment
2. Redis


Usage
-----

1. git clone https://github.com/ritksm/leech.git
2. cd leech
3. pip install -r requirements.txt (You may use virtualenv here)
4. cp leech_devel/local_settings.example.py leech_devel/local_settings.py
4. python manage.py syncdb
5. python manage.py runserver
6. Visit http://localhost:8000/


License
-------
This project is using the MIT License.

Author
------
Jack River (ritksm@gmail.com)


Contribute
----------
You can fork this project and send pull request to me. I would appreciate that.