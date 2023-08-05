django\_shawty
=============

This is an implementation in Django for Shawty webserver integration.  This is a very simple
Django app that adds a single new model that can work with the Shawty Webserver called
ShawtyURL.  This model contains classmethods that allow you to communicate with Shawty and
store/retrieve short URLs.

## PREREQS

django\_shawty requires the following packages to be installed:

[South](http://south.aeracode.org/)

[Requests](http://docs.python-requests.org/en/latest/)

## INSTALLING

You can install django\_shawty simply by running a "pip install django-shawty" and adding
'shawty' to your INSTALLED\_APPS. Then you can run the south migrations to initialize the models
in your database.

## CONFIG

django\_shawty has a set of configurations that you can use to define how to interact with the
Shawty webserver.

SHAWTY\_REQUEST\_URL (string)- The URL of the Shawty server in the form of http://www.shawty.com

SHAWTY\_USE\_DB (bool) - Determine whether or not django\_shawty should 
                         store the shoretened URLs in the DB

SHAWTY\_USE\_CACHING (bool) - Determine whether or not django\_shawty should store/retreive short
                              urls from a cache backend

SHAWTY\_CACHE\_EXPIRE (int) - The time (in seconds) after which the cache for the URL should expire

## Example

To get a new short URL for a set of links, simply invoke the ShawtyURL classmethod "get\_short\_urls"
passing a python list of links.  For example:

    from shawty.models import ShawtyURL
    links = [link1, link2, link3]
    shortenedlinks = ShawtyURL.get\_short\_urls(links)
    print shortened\_links

> {link1:shortlink1, link2:shortlink2, link3:shortlink3}
