==================
django-smoke-admin
==================

django-smoke-admin tests that all admin pages for all registered models responds correctly (HTTP 200).

It uses django-dynamic-fixture for creating fixtures for models.

Installation
------------

First, install django-smoke-admin using pip:

::

    pip install django-smoke-admin

Next, add it to apps in your settings file:

::

    INSTALLED_APPS = (
        ...
        'django-smoke-admin',
    )

Usage
-----

After installation, you can run tests as usual and admin tests will be added to your test set.
