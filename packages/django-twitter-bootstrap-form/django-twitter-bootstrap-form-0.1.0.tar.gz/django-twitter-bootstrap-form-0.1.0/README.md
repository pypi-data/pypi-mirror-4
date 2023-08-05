django-twitter-bootstrap-form
=====================

Implementation of Twitter Bootstrap to Django

Installation
-------------

```
$ pip install django-twitter-bootstrap-form
```

Add new applications at the end of INSTALLED_APPS in your settings.py.

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'twitter_bootstrap_form',
)
```

Usage
---------

```
{% load twitter_bootstrap_form %}

{% block content %}
    <div class="container">
        <div class="row">
            <div class="span12">
                <form method="post" class="form-horizontal">
                    {{ form|as_bootstrap }}
                </form>
            </div>
        </div>
    </div>
{% endblock %}
```

Features
---------

1. Supported django-form-utils fieldsets.
2. Addional classes for form items.