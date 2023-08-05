
=============
Configuration
=============

This section contains information about how to configure your Django projects
to use *sysscope* and also contains a quick reference of the available
*settings* that can be used in order to customize the functionality of this
application.


Configuring your project
========================

In the Django project's ``settings`` module, add ``sysscope`` to the
``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'sysscope',
    )


URLS
====

Add the ``sysscope`` specific URL patterns to the ``urls.py`` file of
your project::

    # URLs for sysscope
    urlpatterns += patterns('',
        url('^sysscope/', include('sysscope.urls')),
    )


Reference of the application settings
=====================================

The following settings can be specified in the Django project's ``settings``
module to customize the functionality of *sysscope*.

``SETTING_A``
    Setting A ...


Synchronize the project database
================================

Finally, synchronize the project's database using the following command::

    python manage.py syncdb

