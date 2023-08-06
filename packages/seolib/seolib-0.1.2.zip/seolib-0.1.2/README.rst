SEO Metrics with no pain
========================



.. image:: https://travis-ci.org/xelblch/seolib.png?branch=master
        :target: https://travis-ci.org/xelblch/seolib

Seolib is a small python library that allows you to get
SEO metrics of your websites with no pain.


Documentation
-------------

Comming soon. Sorry.


Example how to use
------------------

.. sourcecode:: python

    >>> import seolib
    >>> alexa_rank = seolib.get_alexa('http://google.com')
    >>> print alexa_rank
    1
    >>> print seolib.get_google_plus('http://google.com')
    9999


Metrics available
-----------------

- Google +1 count
- Alexa Rank
- Tweets count
- Facebook likes count
- SemRush Top 20 keywords count
- SeoMoz.org free API data (Page Authority, Domain Authority)


Installation
------------

To install seolib open terminal and type:

.. sourcecode:: bash

    $ pip install seolib


Note that it will install requests and lxml libraries too.
Windows users can get vcvarsall.bat error while installing lxml library,
just download it manually from http://www.lfd.uci.edu/~gohlke/pythonlibs/