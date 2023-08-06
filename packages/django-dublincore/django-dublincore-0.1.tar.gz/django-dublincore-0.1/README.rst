django-dublincore
=================

A Django plugin app for applying Dublin Core Metadata to any Django model.


This uses the Django contenttype framework and generic relations to apply a varying number of 
metadata terms to any Django model.

`[Dublin Core Metadata Terms] <http://dublincore.org/documents/dcmi-terms/>`_

Quick start
-----------

1. git clone https://github.com/mredar/django-dublincore.git
2. cd django-dublincore
3. python setup.py install
4. Add "dublincore" to your INSTALLED_APPS setting::

        INSTALLED_APPS = (
                ...
               'dublincore',
        )

5. Run `python manage.py syncdb` to create the dublincore db tables.

6. Start the development server and visit http://127.0.0.1:8000/admin/ to attach some Dublin Core metadata to your objects. (admin app must be installed)

7. Add this to models you wish to add dublincore attributes to::

    from django.contrib.contenttypes import generic
    from dublincore.models import QualifiedDublinCoreElement
    ...

    class Thing(models.Model):
        '''Some Thing
        with dublincore metadata attached
        '''
    	QDCElements = generic.GenericRelation(QualifiedDublinCoreElement)


TODO:

0. Make tests work from clean install
1. improve install process (one cmd)
2. performance analysis - i've read that abstract classes containing datbase fields have a bad performance hit.
3. sample views and usage
4. Better Documentation
5. support dublin core terms (currently just element with "qualifier")
