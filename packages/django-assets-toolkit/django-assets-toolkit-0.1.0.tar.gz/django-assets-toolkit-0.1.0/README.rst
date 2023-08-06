Django Assets Toolkit
=====================

A development toolkit for compiling sass and coffee script files.

Installation
------------

``pip install -U django-assets-toolkit``

Usage
-----

Add ``assetstoolkit`` in your ``INSTALLED_APPS`` settings,
then you can load the ``assetstoolkit`` from your template files which has two template tags:

- ``scss``
- ``coffee``

You can use it in your templates like:

.. code:: python

    {% load assetstoolkit %}

    ...

    <link rel="stylesheet" type="text/css" href="{% scss 'css/styles.scss' %}">
    <script type="text/javascript" src="{% coffee 'src/scripts.coffee' %}"></script>

Have a look at ``settings.py`` to see more options.

Note
----

It will put the compiled sass file in the same directory of .scss file while it'll put the compiled coffee script on the same level where the script is contained but within ``js`` directory. If you want the compiled script to be on a different directory just override ``COFFEE_OUTPUT`` settings which should be sibling of directory where script is located.

For the ``CoffeeScript`` package to work, you need to actually have the `Coffee Script <http://coffeescript.org/>`_ binary in your system.
