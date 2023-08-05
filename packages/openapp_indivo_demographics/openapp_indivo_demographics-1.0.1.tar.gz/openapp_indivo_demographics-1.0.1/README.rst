Demographics
============

This is a Django App which provides a screen to view and edit
the Demographics record.

It is an example / proof of concept application.

There is a dependency on the django-form-admin package. This package
is used to provide a simple forms layer. This package requires the
django.contrib.admin package to be configured.

Installation
------------

Make sure you are in the correct virtualenv environment::

    . python/bin/activate  (or similar)

Configure pre-requisites::

    pip install django-form-admin

Install the package::

    pip install openapp_indivo_demographics

Register the packages.  
Place these lines at the end of the settings.py file in the indivo_ui_server folder::

    import os.path
    import django.contrib
    ADMIN_ROOT_DIR = os.path.dirname(django.contrib.__file__) + "/admin"
    TEMPLATE_DIRS += ADMIN_ROOT_DIR + '/templates/',
    INSTALLED_APPS += 'django.contrib.admin',
    STATICFILES_DIRS += ADMIN_ROOT_DIR + '/static/',

    import formadmin
    FORMADMIN_ROOT_DIR = os.path.dirname(formadmin.__file__)
    TEMPLATE_DIRS += FORMADMIN_ROOT_DIR + '/templates/',
    INSTALLED_APPS += 'formadmin',

    import openapp_indivo.demographics
    DEMOGRAPHICS_ROOT_DIR = os.path.dirname(openapp_indivo.demographics.__file__)
    TEMPLATE_DIRS += DEMOGRAPHICS_ROOT_DIR + '/templates/',
    STATICFILES_DIRS +=  DEMOGRAPHICS_ROOT_DIR + '/static/',
    INSTALLED_APPS += 'openapp_indivo.demographics',

    MIDDLEWARE_CLASSES += 'openapp_indivo.demographics.middleware.GlobalRequestMiddleware',

Restart the server to make sure the configuration is correct.

You have to manually set up the application in the indivo_server
environment. It cannot detect it from the settings file.

Add these two files to the indivo_server environment. 

indivo_server/registered_apps/user/openapp_indivo.demographics/credentials.json::

    {
        "consumer_key": "demographics@apps.openapp.ie",
        "consumer_secret": "demographics"
    }

indivo_server/registered_apps/user/openapp_indivo.demographics/manifest.json::

    {
      "name" : "Demographics",
      "description" : "View and Edit the Demographics record.",
      "author" : "Kevin Gill, OpenApp",
      "id" : "demographics@apps.openapp.ie",
      "version" : "0.1.0",
      "smart_version": "0.0",

      "mode" : "ui",	
      "scope": "record",
      "has_ui": true,
      "frameable": true,

      "icon" :  "/static/openapp_indivo/demographics/images/demographics.png",
      "index": "/openapp_indivo/demographics/start_auth?record_id={record_id}&amp;carenet_id={carenet_id}",
      "oauth_callback_url": "/openapp_indivo/demographics/after_auth"
    }

You have to notify indivo that there is a change to the apps configuration.
Run this command against the indivo_server manage.py::

    python manage.py sync_apps


After this you should be able to add the application to a record.


Outstanding Issues
------------------

Where a record has no Demographics document, an error is produced. I don't know
whether records with Demographics documents are expected or the demo data is 
incomplete.
