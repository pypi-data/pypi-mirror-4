=====================================
Yet Another Restful Django Framework
=====================================

**Yard** is an *API* oriented framework that aims to simplify the developer's work when implementing complex *API design*. It provides a neat, familiar and easy way to control the logic for acceptable parameters in each http-GET-request.


Motivations
-----------

While working with a fairly complex project, with equally complex API design, *Django forms* weren't enough for what was needed. There was still too much code on the resources validating the input parameters. That lead to developing our own resources, inspired by the `Dagny <https://github.com/zacharyvoase/dagny>`_ project, relieving the views from the ugliness of input validations.

With a few extra inspirations, *Yard* was born.

Other frameworks and applications, more mature and solid, such as `Django-Piston <https://bitbucket.org/jespern/django-piston/wiki/Home/>`_, `Tastypie <http://django-tastypie.readthedocs.org/en/latest/>`_ and `Django-Rest-Framework <http://django-rest-framework.org/>`_, can be enough for most needs. But we believe *Yard* brings something new.


Usage
-----------

Here we provide a simple quickthrough in how to setup your project with *Yard*.

**urls.py**

::

    from django.conf.urls.defaults import patterns, include, url
    from views                     import Books
    from yard.urls                 import include_resource

    urlpatterns = patterns('django_yard.app.views.',
        url( r'^books', include_resource( Books ) ),
    )


**params.py**

::

    from yard.forms import *

    class BookParameters:
        year   = IntegerParam( alias='publication_date__year', min=1970, max=2012 )
        title  = CharParam( required=True )
        genre  = CharParam( alias='genres' )
        author = CharParam( alias='author__id' )
        house  = CharParam( alias='publishing_house__id' )

        __logic__ = year, title, genre & (author|house)


**views.py**

::

    from yard.resources import Resource
    from models         import Book

    class Books(Resource):
        # used in the index method
        parameters = BookParameters
        # used in the index and show methods
        fields = ( 'id', 'title', 'publication_date', 'genres', ('author', ('name', 'age',)))

        # index's response metadata
        class Meta:
            maximum = (('longest_title', 'title'),)
            average = (('average_pages', 'number_of_pages'),)

        # index's pagination configuration
        class Page:
            offset_parameter = 'offset'
            results_per_page = {
                'parameter': 'results',
                'default': 25,
                'limit': 50,
            }

        def index(self, request, params):
            #GET /resource/
            return Book.objects.filter( **params )

        def show(self, request, book_id):
            #GET /resource/:id/
            return Book.objects.get( id=book_id )

        def create(self, request):
            #POST /resource/
            return 401, 'You are not authorize'

        def update(self, request, book_id):
            #PUT /resource/:id/
            ...

        def destroy(self, request, book_id):
            #DELETE /resource/:id/
            ...


For more information, please check the documentation available on `Github <http://github.com/laginha/yard>`_.


Contributors
-------------

* `Diogo Laginha <http://github.com/laginha>`_



Thanks also to
---------------

* `David Francisco <http://github.com/dmfrancisco>`_
* `Miguel Laginha <http://github.com/brecke>`_
* `Ricardo Vitorino <http://github.com/rjfv>`_
