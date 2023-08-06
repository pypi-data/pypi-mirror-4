===========
Erlenmeyer
===========

Erlenmeyer allows you to create fully-functional Flask servers, complete with SQLAlchemy models, from a Core Data file.

*It's Flask, SQLAlchemy, and Core Data. Get it? It's a chemistry pun. Get it?*

    $ erlenmeyer -p MegaBits -c MBModels.xcodedatamodeld

This command will generate a new Flask project, called MegaBits, with the following directory structure::

    MegaBits.py
    /handlers
        __init__.py
        ...
    /models
        __init__.py
        ...
    /settings
        settings.json
    /documentation
        MegaBits.html

Where the ellipses (``...``) are lists of models built from your Core Data file.


Flask File
----------

The Flask file (e.g. ``MegaBits.py``) is the primary Flask service. It creates the Flask app and SQLAlchemy instances, and forwards requests to the handler objects found in the ``handlers`` module.

This service has 3 globally accessible variables:

* ``settings``: A dictionary of settings loaded from `settings.json`.

* ``flaskApp``: The Flask app.

* ``database``: The SQLAlchemy instance, loaded from the Flask app.


``handlers``
------------

The ``handlers`` module contains a separate handler object for each model object built from your Core Data file. Every handler has 5+ methods, depending on the relational complexity of the underlying model.

Each handler method retrieves or applies the appropriate information to its underlying model, and returns a cooresponding ``flask.Response`` object, depending on success. In addition, all handler methods are also documented inline.


``models``
----------

The ``models`` module contains object which are created from your Core Data file, and inherit from either ``flask.ext.sqlalchemy.Model`` or their Core Data-stated parent class.


``settings.json``
-----------------

``settings.json`` contains information for the runtime of the service. The "server" dictionary provides information for the Flask app, such as the IP address and port on which to broadcast. And the "sql" dictionary provides SQLAlchemy login and database information with which it should store the models.

Documentation
-------------

The REST API documentation file (e.g. ``MegaBits.html``) is a Twitter Bootstrap-based documentation page. It provides API documentation for each of the URL endpoints laid out in the Flask file.


Other bits...
-------------

For feature requests and bug reports, please use `https://github.com/MegaBits/Erlenmeyer/issues <https://github.com/MegaBits/Erlenmeyer/issues>`_.