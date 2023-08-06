Django Feed Me
==============

[![Build Status](https://travis-ci.org/dstegelman/django-feedme.png?branch=master)](https://travis-ci.org/dstegelman/django-feedme)

Django Feed Me is a replacement for Google Reader.  It keeps track of your feeds, fetches the RSS feeds
and parses them in an easy to read interface.  This is currently in development.  The app works as POC using the Django
Admin.  A seperate interface for adding feeds is coming down in the pipeline.

![image](http://cl.ly/image/0j2z0y0K1e2e/Screen%20Shot%202013-04-27%20at%209.54.10%20AM.png)


Installation
------------

To install FeedMe simply:

    pip install django-feedme

Add ``feedme`` to your installed apps.  Add route a url to ``feedme.urls``

Make sure to syncdb or migrate the app:

    python manage.py syncdb
    python manage.py migrate



If you want to use Celery for fetching (Recommended) then add:

    FEED_UPDATE_CELERY = True

to your settings file.  Make sure you've installed and configured Celery properly.  The syntax used should be good
for both Celery 2 and 3.

This app bundles static and works out of the box with django static files.  If you aren't collecting static
you'll need to copy the static directory to where ever you serve static from.

Celery Beat
-----------

To make use of the Celery beat schedule to automatically update feeds at given intervals, open your settings file and
enter something like the following:

    import datetime


    CELERYBEAT_SCHEDULE = {
        "feed-updates": {
            "task": "update_all_feeds",
            "schedule": datetime.timedelta(hours=1),
            },
        }

More documentation for Celery can be found at the CeleryProject.

Contributions
-------------

Please place all bug reports in Github Issues.  Pull requests are welcome and encouraged!!


Documentation
-------------

Docs are coming soon on RTD.  For now please refer to this file and the Wiki/Issues in this project.


Additional Planned Features
---------------------------

* Import feeds from Google Reader
* Add and manage feeds from the front end (rather than Django Admin)
* Mark all or some feeds as read/unread
* Look and Feel updates
* Tests

Questions/Comments/Hate Mail?
-----------------------------

Drop an issue in Github and I'll be sure to find it.