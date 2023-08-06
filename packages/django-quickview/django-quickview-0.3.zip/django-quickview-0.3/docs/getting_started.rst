django-quickview
================

This documentation is not done. It's a work in progress. Actually I'm trying to find out what format
to write the damn thing in so. "Generic class based views"-like on steroids.

Installation
------------

Install django-quickview in your python environment

.. code:: sh

    $ pip install django-quickview

Add ``quickview`` to your ``INSTALLED_APPS`` setting.

.. code:: python

    INSTALLED_APPS = (
        ...
        'quickview',
    )

Add this to your urls.py.

.. code:: python

  from quickview import discover_views

  urlpatterns = patterns('',)
  urlpatterns += discover_views()

Usage
-----

Create an app called friendslist. Create models in ``model.py``.

.. code:: python

  from django.db import models

  class Friend(models.Model):

      class Meta:
          get_latest_by = "id"

      name = models.CharField(max_length = 100)
      email = models.EmailField(null = True, blank = True)

  class Comment(models.Model):
      friend = models.ForeignKey(Friend, related_name="comments")
      text = models.TextField()
      author = models.CharField(max_length=100)


Define views in ``views.py``.

.. code:: python

    from models import Friend, Comment
    from quickview import ModelQuickView

    class FriendView(ModelQuickView):
        model = Friend
        use_dynamic_ajax_page = True
        use_pagination = True
        items_per_page = 5
        authentication_required = True

        @classmethod
        def get_context(cls, request, *args, **kwargs):
            return {'user': request.user}

        @classmethod
        def view_add_comment(cls, request):
            if request.POST:
                comment = Comment.objects.create(
                    author = request.POST.get('author'),
                    text = request.POST.get('text'),
                    friend = Friend.objects.get(pk=request.POST.get('friend_id'))
                )
                return cls.list(request)
            return cls.render(request, 'comment.html')

.. code:: sh

    $ python manage.py syncdb
    $ python manage.py runserver
