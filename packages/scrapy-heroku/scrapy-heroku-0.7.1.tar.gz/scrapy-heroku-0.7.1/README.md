Scrapy-Heroku
=============

A package to assist with running scrapy on heroku. This is accomplished by providing
a custom application configuration at ``scrapy_heroku.app.application`` that launches
the scrapyd web service using the PORT environment variable and a multi-process work
queue implemented on a Postgres database specified by the DATABASE_URL environment
variable.

Configuration
-------------

Create a git repo that has a scrapy project at the root (scrapy.cfg should be at the
top level). Edit your scrapy.cfg to include the following::

    [scrapyd]
    application = scrapy_heroku.app.application

    [deploy]
    url = http://<YOUR_HEROKU_APP_NAME>.herokuapp.com:80/
    project = <YOUR_PROJECT_NAME>
    username = <A_USER_NAME>
    password = <A_PASSWORD>

Add a requirements.txt file that includes ``scrapy-heroku`` in it. It is strongly
recommended that you version pin scrapy-heroku as well as the version of scrapy that
your project is developed against (pip freeze > requirements.txt). Finally create a
Procfile that consists of::

    web: scrapy server

Make sure you have a postgres database that has been promoted to DATABASE_URL


* Project page: <http://github.com/dmclain/scrapy-heroku>
