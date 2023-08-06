====================
 READ ME, READ ME!!
====================

all the interesting & useful info goes here!!!

====================
    INSTALLATION
====================
to use django-serene simply just do::

>> pip install django-serene

====================
       USAGE
====================
1. In settings.py, add 'djangorestframework' and 'serene' in INSTALLED_APPS
2. The use of serene is very similar to djagnorestframework :)

====================
     CHANGE LOG
====================
Version 0.0.9
--------------------
- Update links function to support instance that is a dict and already has 'links'

Version 0.0.8
--------------------
- Make sure django-serene uses djangorestframework==0.3.3

Version 0.0.7
--------------------
- Change UpdateOrCreateModelMixin to always return Response object

Version 0.0.6
--------------------
- Able to specify sub-fields in 'include' attribute of Serializer/Resource