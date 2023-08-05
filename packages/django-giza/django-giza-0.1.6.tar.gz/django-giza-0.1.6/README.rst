=====================
Django-Sphinx-autodoc
=====================


.. note::

    Original code is from https://github.com/Aquasys/django-sphinx-autodoc
    This version has been cleaned up and modified to work as a Django
    management command.


Django is very nice in that way you can reuse a lot of applications in your
projects. It means for big projects that you'll get a long list of applications
in your settings.INSTALLED_APP.

If you're using Django with Sphinx and want to autodoc all these apps in a wink
of an eye, then this app is for you.

A good combination for documenting your project would be:
 - **sphinx**
 - **cartouche** to avoid polluting your docstrings with rst syntax
 - **django-giza** to generate the doc from your applications
 - **django-sphinxdoc** to integrate the sphinx doc in your website


How it works
------------

It will scrape all your .py files in each application listed by INSTALLED_APPS,
then add automodules in your PROJECT/SPHINX_ROOT/auto_modules.rst.

You will then see your applications grouped in 2 different categories:

- **Project Apps** are applications located in your project directory
- **3rd Party Apps** are apps which are somewhere in your pythonpath
  (preferably in your virtualenv)


Good Practices
--------------

Add a docstring in your application's ``__init__.py`` file to describe it.
django-giza will automatically scrape it for you (although ``__init.__.py``
files are excluded by default...)


Install
-------

``$ pip install django-giza``

Then add ``giza`` to your INSTALLED_APPS in settings.py


Usage
-----

``$ ./manage.py giza``

You can also specify the relative path to your docs root:

``$ ./manage.py giza private/documentation``


Settings
--------

You can modify some of the settings used by django-giza:

- **GIZA_DOCS_ROOT**:
	Root path for documentation (absolute path required).
	  
	defaults to:
	  	``"PROJECT_ROOT/docs"``

- **GIZA_INDEX_DOC**:
	Name of your master document.

	defaults to:
		``"index.rst"``

- **GIZA_FILENAME**:
	Name for the generated modules doc.

	defaults to:
		``"auto_modules"``

- **GIZA_DOC_TITLE**:
	Title for the modules page.

  	defaults to:
		``"Python modules"``

- **GIZA_INTERNAL_TITLE**:
	Title for the internal apps section.

  	defaults to:
		``"Project Apps"``

- **GIZA_EXTERNAL_TITLE**:
	Title for the external apps section.

  	defaults to:
		``"3rd Party Apps"``

- **GIZA_EXCLUDED_APPS**:
	List of applications to exclude. Can use wildcard at the end.

  	defaults to:
    	``["django.*", "giza"]``

- **GIZA_EXCLUDED_MODULES**:
	List of filenames to exclude.
 
  	defaults to:
    	``["__init__.py"]``

- **GIZA_AUTOMODULE_OPTIONS**:
	List of options to the `automodule` directive, such as
	"private-members" (without colon delimiters)

  	defaults to:
		``["deprecated", "members", "private-members", "special-members", "show-inheritance"]``


TODO
----

- Write tests
- improve the not_relevant stuff to auto exclude a file without class or def
