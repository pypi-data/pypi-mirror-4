# Django QuickView

**Putting the nitro into django rapid web development.**

- Author: Thomas Augestad Weholt, <thomas@weholt.org>.
- License: Modified BSD.
- Source: https://bitbucket.org/weholt/django-quickview/src
- Package: https://pypi.python.org/pypi/django-quickview/

- Requirements:
    - Django 1.5
    - Python 2.7.x or 3.3

## Wetting your appetite

In models.py:

    :::python

        from django.db import models
        from quickview import ModelQuickView

        @ModelQuickView
        class Friend(models.Model):

            name = models.CharField(max_length = 100)
            email = models.EmailField(null = True, blank = True)

In global urls.py:

    :::python

        from django.conf.urls import patterns
        from quickview import discover_views

        urlpatterns = patterns('',
        )

        urlpatterns += discover_views()

That's all it takes to get full scaffolding (list, detail, add, update, delete) for your model with similar ajax API. Ok,
you might have to write some templates, but even that can be reduced to a minimum.

## Background

After having used django for a while I noticed that how I worked with my views and urlpatterns followed very similar pattern
and that I should be able to replicate that pattern in a generic way, similar to class based views. My attempts at using
  CBV left me underwhelmed and motivated me to try and come up with a new way of doing things. QuickView are heavily inspired by
  CBV, but takes it all a bit further and removes the need to update urlpatterns all together for most common views. It actually
  removes the common views as well, but gives you the possibility to extend your app by adding custom views. You also get built-in
 ajax support, pagination, authentication and in the future an entire suite of tools to make rapid development using django even easier.

In the end QuickView reduces the time it takes to go from defining a model and getting a site up and running with scaffolding for
your models, with very nice ajax support and generation of templates for your views, styled by using Bootstrap for cross-browser, modern looking
 web sites.

Future development will focus on extending ajax and javascript support to enable users to create pages that don't rely as much on
 the old "request/response by posting/refreshing the whole page"-pattern, by using knockoutjs and handlebarsjs frameworks.


## Installation

    :::python

        pip install django-quickview

In `settings.py` make sure you have the following enabled, which is not by default:

    :::python

        TEMPLATE_CONTEXT_PROCESSORS = (
            ...
            'django.core.context_processors.static', # added this one
            ...
        )

        STATICFILES_FINDERS = (
            ...
            'django.contrib.staticfiles.finders.DefaultStorageFinder', # I commented this one in, was out as default.
            ...
        )

        # Also set the static root
        import os
        STATIC_ROOT = os.path.join(os.path.abspath(os.curdir), 'static')
        if not os.path.exists(STATIC_ROOT):
            os.makedirs(STATIC_ROOT)

        # Finally add quickview to your installed apps:
        INSTALLED_APPS = (
            ...
            'quickview',
            ...)

## Getting started

**NOTE! This assumes you know how django works and at least have followed the basic django tutorial.**

To illustrate how quickview works, take a look at this example. We're going to create a small testproject with one
app in it.

    :::python

        django-admin.py startproject testsite
        cd testsite
        python manage.py startapp friendslist

Add `friendslist` to your installed apps and configure the database setup. In `friendslist/models.py`, define a model looking like this:

    :::python

        from django.db import models

        class Friend(models.Model):

            name = models.CharField(max_length = 100)
            email = models.EmailField(null = True, blank = True)
            address = models.CharField(max_length = 100, null = True, blank = True)
            city = models.CharField(max_length = 100, null = True, blank = True)
            zip_code = models.CharField(max_length = 20, null = True, blank = True)
            country = models.CharField(max_length = 100, null = True, blank = True)
            phone = models.CharField(max_length = 100, null = True, blank = True)


Do a `python manage.py syncdb`. So far we've not done anything but normal django work. To enable a quickview of this model,
add `from quickview import ModelQuickView` at the top models.py and decorate your model like shown below:

    :::python

        from django.db import models
        from quickview import ModelQuickView

        @ModelQuickView
        class Friend(models.Model):

            name = models.CharField(max_length = 100)
            email = models.EmailField(null = True, blank = True)
            address = models.CharField(max_length = 100, null = True, blank = True)
            city = models.CharField(max_length = 100, null = True, blank = True)
            zip_code = models.CharField(max_length = 20, null = True, blank = True)
            country = models.CharField(max_length = 100, null = True, blank = True)
            phone = models.CharField(max_length = 100, null = True, blank = True)


Open the `urls.py` for project, not the one for your app, but the one located alongside `settings.py`. Modify it to look like this:

    :::python

        from django.conf.urls import patterns
        from quickview import discover_views

        urlpatterns = patterns('',
        )

        urlpatterns += discover_views()

Run it with `python manage.py runserver` and head over to `http:\\localhost:8000` in your browser. You should be greeted
with a `Page not found (404)` with the following list:

    :::python

        ^accounts/login/$ [name='login-view']
        ^accounts/logout/$ [name='logout-view']
        ^api/friendslist/friend/get_url/$ [name='api-friendslist-friend-get-url']
        ^friendslist/friend/list/$ [name='friendslist-friend-list']
        ^friendslist/friend/add/$ [name='friendslist-friend-add']
        ^friendslist/friend/(?P<pk>\d+)/$ [name='friendslist-friend-detail']
        ^friendslist/friend/update/(?P<pk>\d+)/$ [name='friendslist-friend-update']
        ^friendslist/friend/delete/(?P<pk>\d+)/$ [name='friendslist-friend-delete']
        ^quickview/debug/$ [name='quickview-debug']

So where did all those urlpatterns come from? Quickview generated those based on the model you decorated. All models get
 5 specific views by default:

  - index
  - add
  - detail
  - update
  - delete

Both the url and the name are based on the same pattern `app_label-model_name-view_name`, except the urls for
detail, update and delete which get the id/pk supplied as part of the request-path. Urlpatterns starting with `^api` are paths
used for ajax-based requests. `^accounts/login/` are enabled to support login/logout and uses the standard django generic views
for authentication. `^quickview/debug/` displays a page showing the same list of urlpatterns as above and are used to debug
your app. It will probably contain more information later on.

If you try to access for instance `http://localhost:8000/friendslist/friend/list/` you'll be greeted with another exception:

    :::html

    TemplateDoesNotExist at /friendslist/friend/list/

You haven't defined any templates for that view to use. It should be located in `friendslist/friend/index.html` in the template-folder
 in your apps-folder. At this point you could stop the django development server and do:

    :::sh

        cd friendslist
        mkdir templates
        cd templates
        mkdir friendslist
        cd friendslist
        mkdir friend

And add a index.html to that last folder and then create templates for detail.html, add.html, update.html and delete.html.

Or you could just do this instead:

    :::sh

        python manage.py generate_templates friendslist Friend

which will generate required templates and give you a starting point for your site in form of a `friendslist/friend/base_site.html` your
templates can extend. The default design is based on Bootstrap and comes with a few javascript goodies we will use in the more advanced user-scenarios
of quickview. The management command will only run once, ie. if the templates-folder exists etc it won't do anything at all.

The syntax for the command is `python manage.py generate_templates app-label model-name1 model-name2 etc`.

The process will also modify your `views.py` file and add a default quickview for the Friend-model so you can go ahead and
remove the `@ModelQuickView`-decorator you added in `models.py`. Now try running the development server again and
refresh `http://localhost:8000/friendslist/friend/list/`. It should show you a rather pretty page where you can add friends etc.
To be able to login you'll have to create some templates as well, but you could use the ones below, placed in a folder
called registration in the root of your templates-folder:

Login.html:

    :::html

        {% extends 'friendslist/friend/base_site.html' %}

        {% block content %}

        <h1>Please login</h1>
        {% if form.errors %}
        <p>Your username and password didn't match. Please try again.</p>
        {% endif %}

        <form method="post" action="{% url 'django.contrib.auth.views.login' %}">
            {% csrf_token %}
            <table>
                <tr>
                    <td>{{ form.username.label_tag }}</td>
                    <td>{{ form.username }}</td>
                </tr>
                <tr>
                    <td>{{ form.password.label_tag }}</td>
                    <td>{{ form.password }}</td>
                </tr>
            </table>

            <input type="submit" value="login" />
            <input type="hidden" name="next" value="{% url 'friendslist-friend-list' %}" />
        </form>
        {% endblock %}


logged_out.html:

    :::html

        {% extends 'friendslist/friend/base_site.html' %}

        {% block content %}

        <h1>You are now logged out</h1>
        <a href="{% url 'friendslist-friend-list' %}">Back to the list</a>
        {% endblock %}

At this point you need to create a user to login, edit the provided templates to better display your data etc. You might also
want to either remove the base_site.html in your `friendslist/templates/friendslist/friend/`-folder or move it to the root
of your templates-folder to use it across apps.

## Advanced use

### Authentication

Probably the easiest thing to enable in a quickview:

    :::python

        class FriendView(ModelQuickView):
            model = Friend
            authentication_required = True

Of course, as mentioned earlier, now you need to provide the generic django views for login and logged_out with some templates,
but examples of such templates are shown above.

### Pagination

The default QuickView generated by using the management command `generate_templates` look like this:

    :::python

        from quickview import ModelQuickView
        from friendslist.models import Friend


        class FriendView(ModelQuickView):
            model = Friend
            use_dynamic_ajax_page = True
            use_pagination = True
            items_per_page = 5
            #authentication_required = True

As you can see it specifies what model to use and several other options. By using the list-view for your model you can enable
pagination of your querysets by setting `use_pagination = True` as seen above. The code uses django's normal pagination support.
To specify a specific page you add a page=page_number to either your form if you POST a request or to the request-url if using GET.
This will also be applied for ajax-calls which will be explained later.

### Ajax

By default QuickView enables some handy javascript functions which will ease working with ajax in your apps. It relies on
jQuery to do most of the heavy lifting, but it also provides you with a very easy to use API for listing, fetching details, adding, updating and deleting
 rows in your database.

You don't have to bother with `csrf_tokens` using this API. Quickview has handled that for you. All communication from the server to the client side
 assumes `JSON` is being used.

If you have a working site from following the instructions in the `Getting started`-section quickview should have generated an API especially
for your model. Our model was called Friend and client-side we have an API called `friendApi` with the following methods and their parameters:

- `list(page, success_handler, failure_handler)`. If no page is specified you'll get the first one. You need to supply a succes_handler since
ajax is async. This function takes one parameter and that is the data generated by the list call, namely a dictionary with a 'object_list'-key
pointing to the list of models. Failure_handler is specified if you want to handle failure to get the list manually. If not it will just be printed to the console by
a dummy handler.

- `details(pk, success_handler, failure_handler)`. Pk is the primary key or id of the object you want. As with list you need to supply a success_handler to
process the call and get hold of the result.

- `add(params, success_handler, failure_handler)`. Params is a dictionary containing data to create a new row in the database. You don't need to
supply a success_handler, but if you do you could handle the data returned by the add-process, which is a dictionary-representation of the newly
created object in addition to an 'added'-value indicating if the object was added or not.

- `update(pk, params, success_handler, failure_handler)`. Pk is the primary key or id of the object you want to update with params. Supply a
 success_handler if you want to handle the updated data related to the model, for instance update the client-side.

- `delete(pk, success_handler, failure_handler)`. Pk is the primary key or id of the object you want to delete. Success_handler can process any response from the server,
which in most cases are a dictionary containing {'deleted': True, 'pk': pk} on success or {'deleted': False, 'pk': pk} on failure.

Adding and updating models using ajax uses the same validation rules as defined in the related form specified on the view. If an ajax call fails
due to validation issues you'll get an response from the server when handling the call in your success_handler looking like:

    :::python

        {'added': false, 'validation_errors': [ .... ] }

If you're running Chrome you can hit CTRL+SHIFT+J and go to the console and type:

    :::javascript

        > friendApi.add({'name': 'Johnny', 'email': j@example.com'})

and hit enter. You should see something like this being printed in the console:

    :::javascript

        Object {object: Object, added: true}

Being able to play around with the javascript ajax API makes it much easier to debug. And fun. Some more examples:

    :::javascript

        > friendApi.list()
          Object {object_list: Array[2]}

        > friendApi.delete(1)
          Object {deleted: true, pk: "1"}

To update an model it gets a bit more complicated, but this example shows how:

    :::javascript

        > friendApi.get(4, function(data){
                data['name'] = 'New name of person';
                friendApi.update(4, data);
          })
          Object {pk: "4", object: Object, updated: true}

The reason for this is simple; doing a simple friendApi.update(4, {'name': 'New name of person'}) would set all other properties
of the model to NULL. This is awkward and I'm hoping to fix this in the future.

**You should really have authentication enabled to avoid abuse of this functionality.**

### Forms, custom forms and pre/post-save hooks

Quickview uses the default form generated from your model. You can override this completly by supplying your own form like this:

    :::python

        class FriendView(ModelQuickView):
            model = Friend
            form = MySpecialForm

You can also specify a set of fields to include or exclude fields like with normal ModelForms:

    :::python

        class FriendView(ModelQuickView):
            model = Friend
            form_fields = ['name', 'email']
            form_fields_to_exclude = ['author']

It normally doesn't make sense to specify both, but you can as with normal ModelForms.

You can also use `hooks`, like pre_save to avoid saving an object by throwing a specific exception or to clean-up data before saving it.
Typical usage is setting some property of the model to request.user. It can be done like this:

    :::python

        @classmethod
        def pre_save(cls, request, obj):
            obj.author = request.user

You always have access to the request itself and you got hooks for pre- and post-save called on add and update and pre- and post-delete
on deletion. To prevent saving you raise `PreSaveException` in pre_save or `PostSaveException` in post_save like this:

    :::python

        @classmethod
        def pre_save(cls, request, obj):
            if obj.text == 'foobar':
                raise PreSaveException('Text cannot be "foobar".')

### Context

To provide context that will be available in all templates rendered by your quickview, you can do this:

    :::python

        class FriendView(ModelQuickView):
            context = {'debug': settings.DEBUG}

If you need access to the request itself to produce the context you can override the get_context-method like so:

    :::python

        @classmethod
            def get_context(cls, request, *args, **kwargs):
                return {'advanced_features_enabled': request.user.is_authenticated()}

### Custom views

To add custom views to your quickview do:

    :::python

        @classmethod
        def view_add_comment(cls, request):
            if request.POST:
                # process the comment stored in request.POST
                # then return to the list
                return cls.list(request)
            return cls.render(request, 'comment.html')

This will add an add_comment-view to your app, available at for instance /friendslist/friend/add_comment/ in our example app.
It uses a utility function called render to produce the actual http-response. You can also provide more context:

    :::python

        return cls.render(request, 'comment.html', context = { .... })

## References

- [1]: http://https://docs.djangoproject.com/en/1.3/ref/class-based-views/
- [2]: http://knockoutjs.com
- [3]: http://handlebarsjs.com
- [4]: http://bootstrap.com