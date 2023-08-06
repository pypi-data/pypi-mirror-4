=========
QuickView
=========

QuickView is sort of a class based view on steriods, which handles basic scaffolding and basic views
in very few lines of code. Take a look at quickview/__init__.py to look at what to override.

The main job is creating necessary templates. It takes care of creating and adding entries in your urls.py as well.

NB! This is a proof-of-concept-release and has ONLY been tested under Python 3.3 and Django 1.5b2.

Quick start
-----------

0. pip install django-quickview.

1. Add "quickview" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'quickview',
      )

2. In your views.py do:

      import quickview

      class YourView(quickview.ModelQuickView);
          model = YourModel # points to a model in models.py

3. In your project urls.py do something like this::

      import quickview
      urlpattern += quickview.discover_views()

3. Run `python manage.py syncdb` to create any models.

4. You'll have to create some templates and put these under yourapp/templates/yourapp/yourmodel or directly in your default templatefolder. The templates are:

    - index.html : lists all your models.
    - detail.html : detail view of one specific instance.
    - add.html : template to add instances.
    - update.html : template to update instances.
    - delete.html : template to delete an instance.

5. Start the development server and visit http://127.0.0.1:8000/yourapp/yourmodel/list/.

Elaboration and motivation
--------------------------

Being somewhat underwhelmed by class based views due to the repetative
coding in urls.py etc I tried to see if I could get generic
scaffolding and basic views up and running based on a given model in
less lines of code. It's pretty simple and not heavily tested, but I'd
like to see if any of you has any inital comments before I spend a lot
of time on it.

The idea is that we always write the same views for alot of our
models; a list view, a detail view and add/update/delete. My
app/urls.py seem to have repeating patterns for all these views.
Generic views, class based or plain functions, do help but I still
find all the coding a bit redundant. In essence the templates are the
only thing that I really have to code manually.

Using quickview you define your model like so :


    class Person(models.Model):
        name = models.CharField(max_length=30)

        age = models.IntegerField(default=10)

In views.py:

    from models import Person

    from quickview import *

    class PersonView(ModelQuickView):
        model = Person

And in urls.py:

    import quickview
    urlpattern += quickview.discover_views()


After a little syncdb and runserver you'll have an urlconfig/pattern
something like this:

    myapp/person/list/$ [name='myapp-person-list']
    myapp/person/add/$ [name='myapp-person-add']
    myapp/person/(?P<pk>\d+)/$ [name='myapp-person-detail']
    myapp/person/update/(?P<pk>\d+)/$ [name='myapp-person-update']
    myapp/person/delete/(?P<pk>\d+)/$ [name='myapp-person-delete']

where myapp is the app my person-models resides in. Now you define
some templates ( list.html, detail.html, add.html, update.html,
delete.html ) in /templates/myapp/person/ and you're good to go ;-).


Todos: user authentication/login_required etc. and unittests.

Version history
---------------

0.2     - Refactored code; QuickView is not dependent on a model. A subclass of QuickView named ModelQuickView takes
          care of all model related magic. This makes it easier to write non-model based views based on the same concept.

0.1     - Initial release.