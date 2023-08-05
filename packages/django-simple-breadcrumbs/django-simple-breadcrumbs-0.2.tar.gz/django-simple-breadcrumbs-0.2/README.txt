===========
Breadcrumbs
===========

Breadcrumbs is a Django application to use breadcrumbs-based navigation.

Using breadcrumbs
-----------------

To use a breadcrumb, load the template tags and specify the breadcrumb::

    {% load breadcrumbs_tags %}
    {% breadcrumb "Title of breadcrumb" url_var %}

Running the tests
-----------------

1. Create and load an isolated Django test environment::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt

2. Run the tests::

    $ ./runtests.py
