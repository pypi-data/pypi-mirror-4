import inspect
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm


class QuickView:
    """
    The base QuickView.
    """
    model = None
    form = None
    context = {}
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
        params = {cls.object_list: cls.get_queryset(request)}
        return render_to_response('%s/%s/index.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

    @classmethod
    def detail(cls, request, *args, **kwargs):
        """
        The default detail-view for this model.
        """
        params = {cls.object_list: cls.get_queryset(request), cls.object_name: cls.get_object(kwargs.get('pk', None))}
        return render_to_response('%s/%s/detail.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

    @classmethod
    def add(cls, request, *args, **kwargs):
        """
        The default view used to add an instance of the assigned model.
        """
        if request.POST:
            form = cls.get_form(request, *args, **kwargs)(request.POST)
            form = cls.form_valid(request, form)
            if form.is_valid():
                obj = form.save(commit=False)
                proceed, obj = cls.pre_save(request, obj)
                if proceed:
                    obj.save()
                    cls.post_save(request, obj)
                return HttpResponseRedirect(reverse('%s-%s-list' % (cls.app_label(), cls.model_name())))
            else:
                params = {'form': form}
                return render_to_response('%s/%s/add.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

        params = {'form': cls.get_form(request, *args, **kwargs)}
        return render_to_response('%s/%s/add.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

    @classmethod
    def update(cls, request, pk, *args, **kwargs):
        """
        The default view used to update an instance of the assigned model.
        """
        obj = cls.get_object(pk)
        if request.POST:
            form = cls.get_form(request, *args, **kwargs)(request.POST, instance = obj)
            if form.is_valid():
                obj = form.save(commit=False)
                proceed, obj = cls.pre_save(request, obj)
                if proceed:
                    obj.save()
                    cls.post_save(request, obj)
                return HttpResponseRedirect(reverse('%s-%s-list' % (cls.app_label(), cls.model_name())))

            params = {'form': form}
        else:
            params = {'form': cls.get_form(request, *args, **kwargs)(instance = obj)}

        return render_to_response('%s/%s/update.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

    @classmethod
    def delete(cls, request, pk, *args, **kwargs):
        """
        The default view used to delete an instance of the assigned model.
        """
        obj = cls.get_object(pk)
        if request.POST:
            if request.POST.get('cancel', False):
                return HttpResponseRedirect(reverse('%s-%s-list' % (cls.app_label(), cls.model_name())))

            if request.POST.get('delete', False):
                proceed, obj = cls.pre_delete(request, obj)
                if proceed:
                    obj.delete()
                    cls.post_delete(request, obj)
                return HttpResponseRedirect(reverse('%s-%s-list' % (cls.app_label(), cls.model_name())))

        params = {cls.object_name: obj}
        return render_to_response('%s/%s/delete.html' % (cls.app_label(), cls.model_name()), cls._get_context(request, params), context_instance = RequestContext(request))

    @classmethod
    def app_label(cls):
        """
        Gets the name of the app the assigned model is residing in.
        """
        return cls.model._meta.app_label.lower()

    @classmethod
    def model_name(cls):
        """
        Gets the name of the assigned model.
        """
        return cls.model._meta.object_name.lower()

    @classmethod
    def get_custom_views(cls):
        """
        Builds an urlpattern for any custom views defined in this view.

        Custom views can be added by adding classmethods to the view like so:

        @classmethod
        def view_custom(cls, request, object_id:int, stype:str):
            return HttpResponse("Object: %s, stype: %s" % (object_id, stype))

        This will add an urlpattern like '/applabel/modelname/custom/(?P<object_id>\d+)/(?P<stype>\w+)/$'
        with the name of 'applabel-modelname-custom'.
        """
        views = []
        for view in [v for v in dir(cls) if 'view_' in v and 'get_custom_views' not in v]:
            v = getattr(cls, view)
            sig = inspect.signature(v)
            _url = '%s/%s/%s/' % (cls.app_label(), cls.model_name(), v.__name__[5:])
            for param in sig.parameters.values():
                if param.name != 'request':
                    if sig.parameters[param.name].annotation == int:
                        _url += '(?P<%s>\\d+)/' % param.name
                    else:
                        _url += '(?P<%s>\\w+)/' % param.name
            _url += '$'
            views.append(url(_url, v, name='%s-%s-%s' % (cls.app_label(), cls.model_name(), v.__name__)))
        return tuple(views)


    @classmethod
    def get_urls(cls):
        """
        Gets all urlpatterns provided by this view. Use it in your urls.py like so:

        class YourView(QuickView):
            model = YourModel

        urlpatterns += YourView.get_urls()
        """
        fields = (cls.app_label(), cls.model_name())
        patterns = (
            url('%s/%s/list/$' % fields, cls.list, name='%s-%s-list' % fields),
            url('%s/%s/add/$' % fields, cls.add, name='%s-%s-add' % fields),
            url('%s/%s/(?P<pk>\d+)/$' % fields, cls.detail, name='%s-%s-detail' % fields),
            url('%s/%s/update/(?P<pk>\d+)/$' % fields, cls.update, name='%s-%s-update' % fields),
            url('%s/%s/delete/(?P<pk>\d+)/$' % fields, cls.delete, name='%s-%s-delete' % fields),
        )

        patterns += cls.get_custom_views()
        return patterns