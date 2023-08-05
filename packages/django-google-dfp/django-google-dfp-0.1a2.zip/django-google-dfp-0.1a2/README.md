Django Google DFP
=======================

Django Google DFP provides template tags for inserting [Google DFP](http://www.google.com/dfp) ad tags.

Installation
------------

Run `pip install django-google-dfp`

Add `google_dpf` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = (
    ...
    'google_dfp',
)
```

Template Tags
-------------

###ad_header
Inserts the JavaScript for serving Google DFP ads. 
*This must go inside the head*


###ad_tag
Inserts the code where the ad will display. It takes an ad unit as an argument. I needs to be in the format `[identifier]_[width]x[height]`.


```html
{% load dfp_tags %}
<html>
    <head>
        <title>My Site</title>
        {% ad_header %}
    </head>
    <body>
        <h1>My Site</h1>
        {% ad_tag 'MYSITE_728x90' %}
        <p>My site's content.</p>
        {% ad_tag 'MYSITE_300x200' %}
    </body>
</html>
```