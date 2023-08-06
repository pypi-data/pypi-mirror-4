django-staticfiles-bootstrap
============================

Easily include twitter bootstrap in your django apps

Installation
------------

    pip install django-staticfiles-bootstrap


Make sure your django project is configured to use staticfiles, then add this to your INSTALLED_APPS

    INSTALLED_APPS += ['django-staticfiles-bootstrap',]

Usage
-----

You can use this in two different ways in your templates

### STATIC_URL

    <link href="{{ STATIC_URL }}bootstrap/css/bootstrap.css" rel="stylesheet">
    <script src="{{ STATIC_URL }}bootstrap/js/bootstrap.js"></script>

### static template tag

    {% load static from staticfiles %}
    <link href="{% static "bootstrap/css/bootstrap.min.css" %}" rel="stylesheet">

Plugins
-------

If you want to use the JavaScript plugins, you will need jQuery. For that, I suggest django-staticfiles-jquery.

Code prettifying requires Google code prettify. For that, I suggest django-staticfiles-google-code-prettify.
