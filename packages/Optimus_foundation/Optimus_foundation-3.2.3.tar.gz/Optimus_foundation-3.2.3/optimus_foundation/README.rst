.. _Foundation: http://github.com/zurb/foundation
.. _modular-scale: https://github.com/scottkellum/modular-scale
.. _Compass: http://compass-style.org/
.. _rvm: http://rvm.io/
.. _Jinja2: http://jinja.pocoo.org/
.. _Jinja2 documentation: http://jinja.pocoo.org/docs/
.. _yui-compressor: http://developer.yahoo.com/yui/compressor/
.. _webassets: https://github.com/miracle2k/webassets
.. _webassets documentation: http://webassets.readthedocs.org/
.. _virtualenv: http://www.virtualenv.org/
.. _Optimus: https://github.com/sveetch/Optimus

This is the default Readme file for your `Optimus`_ project.

Introduction
============

You should put here more details on your project.

This project has been created with a full `Foundation`_ install.

Install
=======

It is recommanded to install it in a `virtualenv`_ environment then install the project dependancies.

Project dependancies are usually in a ``requirements.txt`` file to use with ``pip``.

Example : ::

    virtualenv --no-site-packages my_project
    cd my_project
    source bin/activate
    pip install -r requirements.txt

Foundation
**********

The Foundation install comes from his ruby gem version, so it requires the gems for `Foundation`_ and `modular-scale`_, and so you will have to install a `Compass`_ version if it is not allready installed on your system. See the `Foundation`_ gem install documentation for more details :

    http://foundation.zurb.com/docs/compass.php

This will require a recent `Compass`_ install and so a recent Ruby install too, if you have problem with this you can see to `rvm`_ to install a more recent Ruby version without to touch at your system packages.

A list of the required **gems** is available in the file ``gemsets.txt`` in this project.

Usage
=====

Settings
********

This is where your environment configuration resides, generally the ``settings.py`` is the default settings used in development, and the ``prod_settings.py`` file is used for a production environment that it inherit from the default settings and only set a ``DEBUG = False`` to avoid the debug mode and minify the assets.

`Optimus`_ command line actions allways accept a ``settings`` option to specify a settings file, by default this is the ``settings.py`` that is used but if you want to use another settings file like ``prod_settings.py`` you have to specify it in command line like a Python path : ::

    optimus-cli [ACTION] --settings=prod_settings

If you only want to use the default settings, it's not needed to specify it with ``settings`` option.

Templates
*********

The templates are rendered to pages using template engine `Jinja2`_.

For each template the default context variables are :

* **debug** : A boolean, his value come from ``settings.DEBUG``;
* **SITE** : A dict containing some variables from the settings;

  * **name** : the value from ``settings.SITE_NAME``;
  * **domain** : the value from ``settings.SITE_DOMAIN``;
  * **web_url** : the value from ``settings.SITE_DOMAIN`` prefixed by *http://*;

* **STATIC_URL** : A string, containing the value from ``settings.STATIC_URL``;

Read the `Jinja2 documentation`_ for more details.

Assets
******

You can simply put your assets where you want in the ``sources`` directory and add your assets directories in ``settings.FILES_TO_SYNC``, they will be copied to your build directory.

But with Optimus this is only required for *real* static assets like images. For CSS and Javascript you should manage them with `webassets`_ that is allready installed with Optimus.

With `webassets`_ you manage your assets as **packs** named ``Bundle``, like a bundle for your main CSS, another for your IE CSS hacks/patchs and another for your Javascripts files. You will have to register your custom bundles in ``settings.EXTRA_BUNDLES`` and enable them in ``settings.ENABLED_BUNDLES``.

The benefit of `webassets`_ is that it can pre and post process all your assets, this is usually used to *minify* and pack multiple files in one final file. Read the `webassets documentation`_ for more details to use this and to manage bundle assets in your templates.

Compass
-------

Note that this project use Compass to compile his SCSS souces to CSS files, you should not directly edit your CSS files but instead edit SCSS sources and build them with `Compass`_.

It is recommanded to simply use the *watch* action command from `Compass`_ to watch for your changes on SCSS sources to automatically rebuild them.

Pages
*****

The pages to build are registred as ``Page`` object usually in a ``pages.py`` file in your project. It must contains a ``PAGES`` variable that is a list of all page to build.

This list contains ``Page`` instances, see ``optimus.builder.pages`` to understand how you can manage your content, templates, etc..

Building
********

Configure your settings if needed, then your pages to build and finally launch optimus to build them : ::

    optimus-cli build

After the first build, you can use the ``watch`` command action to automatically rebuild 
files at each change in your sources.

