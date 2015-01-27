vote_tool
=========

A site to help people decide how to vote for the knesset (work in progress)

The site is currently running at http://azlemi.org.il/

How to set up your own local development environment
====================================================

In the shell - run:

    $ git clone --recursive https://github.com/yairchu/vote_tool.git
    $ cd vote_tool
    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    (venv)$ pip install -r requirements.txt
    (venv)$ python manage.py migrate
    (venv)$ python manage.py runserver

At this stage you should be running your own local instance running on your computer serving pages at [http://localhost:8000](http://localhost:8000)
