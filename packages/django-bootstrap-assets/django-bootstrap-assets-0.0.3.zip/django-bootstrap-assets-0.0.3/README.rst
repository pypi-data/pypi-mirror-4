=======================
django-bootstrap-assets
=======================

Collection of static assets (CSS, JavaScript, images) that allow for quickly
adding Twitter bootstrap and related plugins to a Django project.

jQuery is also included with the assets. Although the project is released under
Apache License 2.0, jQuery is covered separately by MIT license. See LICENSE
and LICENSE-jQuery files for more details.

Installation
============

To install, use pip or easy_install:

    pip install django-bootstrap-assets

Next, add one of the preferred pluggable apps to ``INSTALLED_APPS``. For
example, if we want to install Bootstrap and all of the plugins at once::

    INSTALLED_APPS = (
        ...
        'bootstrap_all',
        ...
    )

Apps are explained in `Structure of the packages`_ section. 

Included plugins
================

Following two plugins are included:

+ select2_
+ bootstrap-datepicker_

Structure of the packages
=========================

This project is divided into four packages. Each package contains a pluggable
Django app which provides static assets.

+ ``bootstrap``: contains Twitter bootstrap only
+ ``bootstrap_select2``: contains select2 plugin
+ ``bootstrap_datepicker``: contains the datepicker plugin
+ ``bootstrap_all``: contains all of the above

Each package has normal Django app structure with a ``static`` directory
containing the assets.

The ``bootstrap_all`` app simply contains symlinks to all of the assets in
other three apps.

.. _select2: http://ivaynberg.github.com/select2/
.. _bootstrap-datepicker: http://www.eyecon.ro/bootstrap-datepicker/
