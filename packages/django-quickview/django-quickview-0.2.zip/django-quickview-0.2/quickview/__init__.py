import inspect
from django.conf import settings
from django.conf.urls import url
from django.core.urlresolvers import reverse, resolve, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm


class QuickView(object):
    context = {}
    model_name = None
    app_label = None
    model = None
    authentication_required = False

    @classmethod
    def get_context(cls, request, *args, **kwargs):
        """
        Gets an empty dict as default context. Override and return a custom dict to add extra context.
        """
        return {}

    @classmethod
    def _get_context(cls, request, params, *args, **kwargs):
        """
        Internal method that builds a final context based on the get_context-method and any classbased context.
        """
        cntx = {}
        cntx.update(params)
        cntx.update(kwargs)
        cntx.update(cls.context)
        cntx.update(cls.get_context(request, *args, **kwargs))
        return cntx

    @classmethod
    def render(cls, request, template_name = None, context = {}):
        """
        Returns a response-object based on the given request, template and optional context.
        """
        if not template_name:
            template_name = "%s.html" % resolve(request.path).view_name[5:]
        return render_to_response(cls.build_template_path(template_name), cls._get_context(request, context), context_instance = RequestContext(request))

    @classmethod
    def _app_label(cls):
        """
        Gets the name of the app the assigned model is residing in.
        """
        if cls.app_label:
            return cls.app_label

        if not cls.model:
            return

        return cls.model._meta.app_label.lower()

    @classmethod
    def _model_name(cls):
        """
        Gets the name of the assigned model.
        """
        if cls.model_name:
            return cls.model_name

        if not cls.model:
            return

        return cls.model._meta.object_name.lower()


    @classmethod
    def _get_custom_views(cls):
        """
        Builds an urlpattern for any custom views defined in this view.

        Custom views can be added by adding classmethods to the view like so:

        @classmethod
        def view_custom(cls, request, object_id:int, stype:str):
            return HttpResponse("Object: %s, stype: %s" % (object_id, stype))

        For views with modelname specified:
        This will add an urlpattern like '/applabel/modelname/custom/(?P<object_id>\d+)/(?P<stype>\w+)/$'
        with the name of 'applabel-modelname-custom'.

        If modelname is omitted:
        '/applabel/custom/(?P<object_id>\d+)/(?P<stype>\w+)/$'
        with the name of 'applabel-custom'.
        """
        views = []
        for view in [v for v in dir(cls) if 'view_' in v and '_get_custom_views' not in v and 'build_view_name' not in v]:
            v = getattr(cls, view)
            sig = inspect.signature(v)
            _url = cls.build_url(v.__name__[5:])
            for param in sig.parameters.values():
                if param.name != 'request':
                    if sig.parameters[param.name].annotation == int:
                        _url += '(?P<%s>\\d+)/' % param.name
                    else:
                        _url += '(?P<%s>\\w+)/' % param.name
            _url += '$'
            views.append(url(_url, v, name=cls.build_view_name(v.__name__)))

        return tuple(views)

    @classmethod
    def build_template_path(cls, template_name):
        """

        """
        return "/".join(cls._get_parts(template_name))

    @classmethod
    def build_url(cls, view_name):
        """

        """
        return "^%s/" % "/".join(cls._get_parts(view_name))

    @classmethod
    def build_view_name(cls, view_name):
        """

        """
        return "-".join(cls._get_parts(view_name))

    @classmethod
    def _get_parts(cls, last_part):
        parts = []
        if cls._app_label():
            parts.append(cls._app_label())

        if cls._model_name():
            parts.append(cls._model_name())

        parts.append(last_part)
        return parts

    @classmethod
    def get_urls(cls):
        """

        """
        return cls._get_custom_views()


class ModelQuickView(QuickView):
    """
    The base QuickView.
    """
    form = None
    queryset = None
    object_list = "object_list"
    object_name = "object"

    @classmethod
    def get_queryset(cls, request, *args, **kwargs):
        """
        Gets the default queryset for the assigned model.
        """
        return cls.model.objects.all()

    @classmethod
    def pre_save(cls, request, obj):
        """
        Called before any save operations coming from add or update.
        Can be used for validation to avoid saving invalid objects by
        returning a tuple of (False, obj).
        """
        return True, obj

    @classmethod
    def post_save(cls, request, obj):
        """
        Called after any save operations coming from add or update.
        """
        return obj

    @classmethod
    def pre_delete(cls, request, obj):
        """
        Called before any delete. Can be used for validation to avoid deleting objects,
        by returning a tuple if (False, obj) instead of (True, obj).
        """
        return True, obj

    @classmethod
    def post_delete(cls, request, obj):
        """
        Called after any delete.
        """
        return obj

    @classmethod
    def form_valid(cls, request, form):
        """
        Performs any custom validation of your form.
        """
        return form

    @classmethod
    def get_object(cls, pk):
        """
        Returns an instance related to the supplied primary key or raises 404 if not found.
        """
        try:
            return cls.model.objects.get(pk=pk)
        except Exception as e:
            raise Http404()

    @classmethod
    def get_form(cls, request, *args, **kwargs):
        """
        Gets the default form for the assigned model used in add and update views.
        """
        if cls.form:
            return cls.form

        class _Form(ModelForm):
            class Meta:
                model = cls.model

        return _Form

    @classmethod
    def list(cls, request, *args, **kwargs):
        """
        The default list-view for this model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        params = {cls.object_list: cls.get_queryset(request)}
        return cls.render(request, 'index.html', params)

    @classmethod
    def detail(cls, request, *args, **kwargs):
        """
        The default detail-view for this model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        params = {cls.object_list: cls.get_queryset(request), cls.object_name: cls.get_object(kwargs.get('pk', None))}
        return cls.render(request, 'detail.html', params)

    @classmethod
    def add(cls, request, *args, **kwargs):
        """
        The default view used to add an instance of the assigned model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        if request.POST:
            form = cls.get_form(request, *args, **kwargs)(request.POST)
            form = cls.form_valid(request, form)
            if form.is_valid():
                obj = form.save(commit=False)
                proceed, obj = cls.pre_save(request, obj)
                if proceed:
                    obj.save()
                    cls.post_save(request, obj)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))
            else:
                params = {'form': form}
                return cls.render(request, 'add.html', params)

        params = {'form': cls.get_form(request, *args, **kwargs)}
        return cls.render(request, 'add.html', params)

    @classmethod
    def update(cls, request, pk, *args, **kwargs):
        """
        The default view used to update an instance of the assigned model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        obj = cls.get_object(pk)
        if request.POST:
            form = cls.get_form(request, *args, **kwargs)(request.POST, instance = obj)
            if form.is_valid():
                obj = form.save(commit=False)
                proceed, obj = cls.pre_save(request, obj)
                if proceed:
                    obj.save()
                    cls.post_save(request, obj)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

            params = {'form': form}
        else:
            params = {'form': cls.get_form(request, *args, **kwargs)(instance = obj)}

        return cls.render(request, 'update.html', params)

    @classmethod
    def delete(cls, request, pk, *args, **kwargs):
        """
        The default view used to delete an instance of the assigned model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        obj = cls.get_object(pk)
        if request.POST:
            if request.POST.get('cancel', False):
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

            if request.POST.get('delete', False):
                proceed, obj = cls.pre_delete(request, obj)
                if proceed:
                    obj.delete()
                    cls.post_delete(request, obj)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

        params = {cls.object_name: obj}
        return cls.render(request, 'delete.html', params)

    @classmethod
    def get_urls(cls):
        """
        Gets all urlpatterns provided by this view. Use it in your urls.py like so:

        class YourView(QuickView):
            model = YourModel

        urlpatterns += YourView.get_urls()
        """
        fields = (cls._app_label(), cls._model_name())
        patterns = (
            url(cls.build_url('list'), cls.list, name=cls.build_view_name('list')),
            url(cls.build_url('add'), cls.add, name=cls.build_view_name('add')),
            url(cls.build_url('(?P<pk>\d+)'), cls.detail, name=cls.build_view_name('detail')),
            url(cls.build_url('update/(?P<pk>\d+)'), cls.update, name=cls.build_view_name('update')),
            url(cls.build_url('delete/(?P<pk>\d+)'), cls.delete, name=cls.build_view_name('delete')),
        )

        patterns += cls._get_custom_views()
        return patterns


def discover_views(add_auth_pattern = True):
    """
    Discovers all quickviews in all installed apps and adds required urls.
    """
    urlpatterns = add_auth_pattern and (url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login-view'),) or ()
    apps = [ app for app in settings.INSTALLED_APPS if not "django" in app ]
    for app in apps:
        views = __import__('%s.views' % app, globals(), locals())
        for d in dir(views.views):
            m = getattr(views.views, d)
            if not inspect.isclass(m):
                continue

            if issubclass(m, QuickView) and m is not QuickView and m is not ModelQuickView:
                urlpatterns += m.get_urls()

    return urlpatterns

