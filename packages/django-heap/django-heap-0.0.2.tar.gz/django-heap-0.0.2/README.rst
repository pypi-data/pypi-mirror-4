===========
django-heap
===========

Heap is a unique new service that automatically captures all user actions on
your site including UI interaction.

This library helps developers integrate `Heap analytics`_ into their Django
projects.

Installation
============

Install using pip::

    pip install django-heap

Basic usage
===========

Add ``heap`` to installed apps::

    INSTALLED_APPS = (
        ...
        'heap',
    )

There is no need to run ``manage.py syncdb`` since django-heap has no database
tables. Add the ``heap`` context processor::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'heap.context_processors.heap',
    )

Finally, configure the app ID in ``settings.py``::

    HEAP_APP_ID = '12345...'

To enable Heap tracking, you must include the script tag snippet in your
template like so::

    <head>
        ....
        {% include 'heap/script.html' %}
    </head>

Now you are ready to start tracking.

Tracking superusers
===================

By default, django-heap tracks your site's superusers as well. You can disable
this by setting the ``HEAP_TRACK_SUPERUSER`` flag to ``False``. This prevents
the script tag template from rendering when user has ``is_superuser`` property
set to ``True``.

Automatic identification of users
=================================

django-heap can automatically call ``heap.identify`` with data from the
authenticated user. To do that, you need to set the ``HEAP_AUTO_ID_USER``
setting to ``True`` (disabled by default). Only authenticated users will be
identify. The User object's ``get_full_name`` method will be used to derive the
``name`` parameter for the ``identify`` call, and if User object has an
``email`` field, the ``email`` parameter will also be passed. There is
currently no handling for the cases where ``get_full_name`` returns the user's
``email`` address.

**Note** This implementation is currently experimental, so please do it
manually in the ``BODY`` tag as suggested by Heap documentation if you find it 
doesn't work for you.

Customizing django-heap
=======================

You can customize django-heap by simply overriding the default template. There
is currently no direct support for custom tracking calls, but it is planned for
the next release.

Reporting bugs
==============

Please report bugs to our BitBucket `issue tracker`_.

.. _Heap Analytics: https://heapanalytics.com/
.. _issue tracker: https://bitbucket.org/monwara/django-heap/issues
