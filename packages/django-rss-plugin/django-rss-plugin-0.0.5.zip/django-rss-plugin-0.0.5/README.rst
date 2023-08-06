=====================
Django CMS RSS Plugin
=====================

Simple plugin to show a a rss feed in your django cms site.

Features
========
* Show specified number of feeds in the page.
* You can choose to open the feed in current window or new window.
* Show any rss feed you specified.
* The feed list would be cached for specified time long.

Usage
=====

Installation::

  $ pip install django-rss-plugin

Add rssplugin to your INSTALLED_APPS in Django settings.py file, Like following::

  INSTALLED_APPS=(
  	'rssplugin',
  )

**template filter**

#. parsed_to_date::

    {% load rss_tags %}
    {{ entry.published_parsed|parsed_to_date|timesince }}

see rss.html for usage examples.

Online Resources
----------------

* `Code repository`_.

.. _Code repository: https://github.com/zgwmike/django-rss-plugin
