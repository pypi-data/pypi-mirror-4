Incuna Storages
===============

A collection of django storage backends primarily used to set the location of files in the remote backend.

Installation
------------
Using your favourite package manager: ::

    pip install incuna_storages

Add to your ``INSTALLED_APPS``: ::

    ...
    'incuna_storages',
    ...


Usage
-----
Set your storage backend to one of the included classes: ::

    DEFAULT_FILE_STORAGE = 'incuna_storages.backends.S3MediaStorage'
    STATICFILES_STORAGE = 'incuna_storages.backends.S3StaticStorage'


Dependencies
------------
The included classes are built on top of existing packages. No assumptions have been made on which classes you'll be using so nothing has been added to ``required_packages``.

Since you'll probably need other bits from the packages anyway it's been left up to you, the intrepid developer, to deal with the dependencies yourself.

