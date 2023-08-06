django-wunderground
=================

NOTE: This project, forked from MegaMark16, was made more generic,
as it includes a template tag that can look up weather by ZIP code.

An extension for Django CMS that pulls current weather information
based on the website visitor's IP address and displays it on the 
screen.  You will need a www.wunderground.com API key to use this.

Dependancies
============

- django (tested with 1.4)
- django-cms (tested with 2.3.5)
- django-classy-tags (tested with 0.4)

Getting Started
=============

To get started simply install using ``pip``:
::
    pip install django-wungerground

Add ``wunderground`` to your installed apps.

Add WUNDERGROUND_KEY to your settings file.  
::
    WUNDERGROUND_KEY = 'abcdefgh12345678'
	
Usage
=============

Simply drop a Current Local Weather plugin on a page.  You will probably
want to override the ``wunderground/local_weather.html`` 
or ``wunderground/local_weather_tag.html`` 
templates.  Any of the fields from the wunderground.com "conditions" api
call should be available in the template under the context variable 
``weather_info``.

Template tag
-------------

This library provides a simple template tag:
::
    {% current_weather %}

When provided with a variable, it attempts to look it up using WUnderground's
geocode API, which usually expects a ZIP/Postal code:
::
    {% current_weather '04421' %}

Will display the weather in Castine, Maine.
