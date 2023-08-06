.. -*- restructuredtext -*-

Installation instructions
=========================

Requirements
------------
* Python >= 2.5 or Python 3
* `Sphinx <http://www.sphinx-doc.org/>`_ 1.1 or newer.

Installing
----------

* To install from pypi using pip::

    pip install epfl-sphinx-theme

* To install from pypi using easy_install::

    easy_install epfl-sphinx-theme
    
* To install from source using ``setup.py``::

    python setup.py build
    sudo python setup.py install

.. index:: readthedocs.org; installation on

ReadTheDocs
-----------
To use this theme on `<http://readthedocs.org>`_:

1. If it doesn't already exist, add a pip ``requirments.txt`` file to your documentation (e.g. alongside ``conf.py``).
   It should contain a minimum of the following lines::

       sphinx
       epfl_theme

   ... as well as any other build requirements for your project's documentation.

2. When setting up your project on ReadTheDocs, enter the path to ``requirements.txt``
   in the *requirements file* field on the project configuration page.

3. ReadTheDocs will now automatically download the latest version of :mod:`!cloud_sptheme`
   when building your documentation.

Configuring: conf.py
--------------------

Once installed you should change your Sphinx ``conf.py`` to include::

    import epfl_theme
    html_theme = 'epfl'
    html_theme_path = [epfl_theme.get_theme_dir()]
