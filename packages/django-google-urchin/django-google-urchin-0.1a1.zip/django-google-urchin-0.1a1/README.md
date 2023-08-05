Django Google Analytics
=======================

Django Google Analytics provides a template tag for inserting the tracking code to provide [Google Analytics](http://www.google.com/analytics/) data.

Installation
------------

Run `pip install django-google-analytics`

Add `google_analytics` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = (
    ...
    'google_analytics',
)
```

Template Tags
-------------

###google_analytics
Inserts the Google Analytics' tracking code in your template. Takes the tracking code as an argument.

```html
{% load analytics %}
<html>
    <head>
        <title>My Site</title>
    </head>
    <body>
        <h1>My Site</h1>
        <p>My site's content.</p>
        {% google_analytics 'UA-XXXXXXX-XX' %}
    </body>
</html>
```