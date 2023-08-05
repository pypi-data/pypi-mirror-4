=============
pinscher-core
=============

Pinscher is a collection of software that manages password collections. Pinscher helps you store and retrieve passwords for as many accounts as you like. It can also create random (complex) passwords for you so you can easily have a different password for each account you own.

Your username and password details are stored in strongly encrypted files so you don't have to worry about them being stolen. These encrypted files can be kept on cloud services like Dropbox_ or `Google Drive`_. This way you can share passwords across all of your computers and devices.

.. _Dropbox: https://www.dropbox.com/
.. _Google Drive: https://drive.google.com/

What's pinscher-core?
---------------------

Pinscher-core is the set of Python functions that can interact with the Pinscher password files. Using the functions in this module you can insert, update, delete and list passwords, usernames and domains. This module is not intended for end-users, it's intended for developers who wish to include Pinscher password storage in their Python software. For more user-friendly software visit http://pinscher.williammayor.co.uk.

Getting pinscher-core
---------------------

The easiest way is to use pip:

    $ pip install pinscher-core

I would recommend getting virtualenv_ as well. It makes for really easy environment and dependency management.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

Without pip
...........

You can get the source code from the `GitHub repo`_.

.. _GitHub repo: https://github.com/WilliamMayor/pinscher

*or*

You can download the source using easy_install:

    $ easy_install pinscher-core

Again, virtualenv_ is recommended.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

*or*

You can download the files directly from PyPi_ or the `Pinscher homepage`_.

.. _PyPi: http://pypi.python.org/pypi/pinscher-core/
.. _Pinscher homepage: http://pinscher.williammayor.co.uk

Dependencies
````````````

Pinscher-core relies on PyCrypto_. If you use pip to install the module then you don't need to worry about installing this. If you use one of the other methods then you'll need to follow the installation instructions on the PyCrypto page to go about getting yourself a copy.

.. _PyCrypto: http://pypi.python.org/pypi/pycrypto
