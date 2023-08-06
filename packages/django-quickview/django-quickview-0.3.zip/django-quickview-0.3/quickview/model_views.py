from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.template.response import SimpleTemplateResponse
from quickview.core_views import *
from quickview.exceptions import *
from quickview import ViewRegistration


class ModelQuickView(QuickView):
    """
    The base QuickView.
    """
    form = None
    queryset = None
    object_list = "object_list"
    object_name = "object"
    views_to_create = ['list', 'detail', 'add', 'update', 'delete']
    items_per_page = 25
    use_pagination = False
    use_dynamic_ajax_page = False
    form_fields = None
    form_fields_to_exclude = None

    def __new__(typ, model, *args, **kwargs):
        """
        Now the class can be used as a decorator as well :-):

        @ModelQuickView
        class YourModel(models.Model):
            name = models.CharField(max_length = 10)

        """
        klass = type('%sView' % model._meta.object_name, (ModelQuickView,), {})
        setattr(klass, 'model', model)
        ViewRegistration.register(klass)
        return model

    @classmethod
    def dictify_queryset(cls, qs, fields=[], exclude=[]):
        """
        Returns a list of dictionaries created from a queryset or list of model instances.
        """
        result = []
        for element in qs:
            result.append(model_to_dict(element, fields = fields, exclude = exclude))
        return result

    @classmethod
    def get_queryset(cls, request, *args, **kwargs):
        """
        Gets the default queryset for the assigned model.
        """
        return cls.model.objects.all()

    @classmethod
    def pagination(cls, request):
        """
        Returns a pagination object based on a request and related model.
        """
        object_list = cls.get_queryset(request)
        paginator = Paginator(object_list, cls.items_per_page)
        page = request.is_ajax() and request.POST.get('page') or request.GET.get('page')
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        return objects

    @classmethod
    def pre_save(cls, request, obj):
        """
        Called before any save operations coming from add or update.
        Can be used for validation to avoid saving invalid objects by
        returning a tuple of (False, obj).
        """
        pass

    @classmethod
    def post_save(cls, request, obj):
        """
        Called after any save operations coming from add or update.
        """
        pass

    @classmethod
    def pre_delete(cls, request, obj):
        """
        Called before any delete. Can be used for validation to avoid deleting objects,
        by returning a tuple if (False, obj) instead of (True, obj).
        """
        pass

    @classmethod
    def post_delete(cls, request, obj):
        """
        Called after any delete.
        """
        pass

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
                fields = cls.form_fields
                exclude = cls.form_fields_to_exclude

        return _Form

    @classmethod
    def list(cls, request, *args, **kwargs):
        """
        The default list-view for this model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        if request.is_ajax():
            params = {cls.object_list: cls.use_pagination and cls.dictify_queryset(cls.pagination(request)) or
                                       cls.dictify_queryset(cls.get_queryset(request))}
            return cls.ajax_response(request, params)

        params = {cls.object_list: cls.use_pagination and cls.pagination(request) or cls.get_queryset(request)}
        return cls.render(request, 'index.html', params)

    @classmethod
    def detail(cls, request, *args, **kwargs):
        """
        The default detail-view for this model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        if request.is_ajax():
            params = model_to_dict(cls.get_object(kwargs.get('pk', None)), fields=[], exclude=[])
            return cls.ajax_response(request, params)

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
                try:
                    obj = form.save(commit=False)
                    cls.pre_save(request, obj)
                    obj.save()
                    cls.post_save(request, obj)
                except (PreSaveException, PostSaveException) as ex:
                    if request.is_ajax():
                        return cls.ajax_response(request, {'added': False, 'message': ex})

                    params = {'form': form, 'message': ex}
                    return cls.render(request, 'add.html', params)

                if request.is_ajax():
                    params = {cls.object_name: model_to_dict(obj, fields=[], exclude=[]), 'added': True}
                    return cls.ajax_response(request, params)

                redirect_url = request.POST.get('redirect_url', None)
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

            else:
                if request.is_ajax():
                    return cls.ajax_response(request, {'added': False, 'validation_errors': form._errors})

                params = {'form': form, 'message': None}
                return cls.render(request, 'add.html', params)


        if request.is_ajax():
            raise Http404()

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
                try:
                    obj = form.save(commit=False)
                    cls.pre_save(request, obj)
                    obj.save()
                    cls.post_save(request, obj)
                except (PreSaveException, PostSaveException) as ex:
                    if request.is_ajax():
                        return cls.ajax_response(request, {'updated': False, 'pk': pk, 'message': ex})

                    params = {'form': form, 'message': ex}
                    return cls.render(request, 'update.html', params)

                if request.is_ajax():
                    params = {cls.object_name: model_to_dict(obj, fields=[], exclude=[]), 'updated': True, 'pk': pk}
                    return cls.ajax_response(request, params)

                redirect_url = request.POST.get('redirect_url', None)
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

            else:
                if request.is_ajax():
                    return cls.ajax_response(request, {'pk': pk, 'update': False, 'validation_errors': form._errors})

                params = {'form': form, 'message': None, cls.object_name: obj}
                return cls.render(request, 'update.html', params)

        if request.is_ajax():
            raise Http404()

        params = {'form': cls.get_form(request, *args, **kwargs)(instance = obj), cls.object_name: obj}
        return cls.render(request, 'update.html', params)

    @classmethod
    def delete(cls, request, pk, *args, **kwargs):
        """
        The default view used to delete an instance of the assigned model.
        """
        if cls.authentication_required and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login-view'))

        if request.POST.get('cancel', False):
            if request.is_ajax():
                raise Http404()

            return HttpResponseRedirect(reverse(cls.build_view_name('list')))

        obj = cls.get_object(pk)
        if request.POST:
            if request.POST.get('delete', False):
                try:
                    cls.pre_delete(request, obj)
                    obj.delete()
                    cls.post_delete(request, obj)
                except (PreDeleteException, PostDeleteException) as ex:
                    if request.is_ajax():
                        return cls.ajax_response(request, {'deleted': False, 'pk': pk, 'message': ex})

                    params = {cls.object_name: obj, 'message': ex}
                    return cls.render(request, 'delete.html', params)

                if request.is_ajax():
                    return cls.ajax_response(request, {'deleted': True, 'pk':pk})

                redirect_url = request.POST.get('redirect_url', None)
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
                return HttpResponseRedirect(reverse(cls.build_view_name('list')))

        if request.is_ajax():
            raise Http404()

        params = {cls.object_name: obj}
        return cls.render(request, 'delete.html', params)

    @classmethod
    def ajax_view_get_url(cls, request):
        """

        """
        if not request.POST or not request.is_ajax():
            raise Http404()

        try:
            _url = request.POST.get('url')
            _args = request.POST.getlist('args[]')
            url = reverse(_url, args=_args)
        except (Exception) as e:
            return cls.ajax_response(request, {'message': e})
        return cls.ajax_response(request, {'url': url})

    @classmethod
    def dynamic_ajax_page(cls, request):
        """
        Returns a dynamically built javascript page with ajax functions related to model.
        """
        ajax_views = []
        for view_name in cls._get_custom_ajax_views():
            ajax_views.append(view_name)

        model_name = cls.model._meta.object_name.lower()
        params = {
            'app_label': cls.model._meta.app_label.lower(),
            'model_names': [model_name],
            'field_names': {model_name:get_field_names_from_model(cls.model)},
            'ajax_views': ajax_views
        }

        return SimpleTemplateResponse(
            template = 'quickview/quickview_model_api.js',
            context = params,
            content_type = "text/javascript"
        )

    @classmethod
    def debug_view(cls, request):
        """
        Returns a page showing what urls will be generated from registered quickviews. And probably more in the future.
        """
        views = []
        for view in ViewRegistration.registered_views.values():
            views.extend(view.get_urls())

        context = {
            'generated_urls': [{'url': urlregex._regex, 'function': urlregex._callback.__name__, 'name': urlregex.name} \
                               for urlregex in views],
        }

        return render_to_response('quickview/debug.html', context, context_instance = RequestContext(request))

    @classmethod
    def get_urls(cls):
        """
        Gets all urlpatterns provided by this view. Use it in your urls.py like so:

        class YourView(QuickView):
            model = YourModel

        urlpatterns += YourView.get_urls()
        """
        patterns = list(cls._get_custom_views())
        if cls.use_dynamic_ajax_page:
            patterns.append(url(cls.build_url(None, prefix = 'api') + '/javascript.js$', cls.dynamic_ajax_page, name=cls.build_view_name('api')))

        if 'list' in cls.views_to_create:
            patterns.append(url(cls.build_url('list/$'), cls.list, name=cls.build_view_name('list')))

        if 'add' in cls.views_to_create:
            patterns.append(url(cls.build_url('add/$'), cls.add, name=cls.build_view_name('add')))

        if 'detail' in cls.views_to_create:
            patterns.append(url(cls.build_url('(?P<pk>\d+)/$'), cls.detail, name=cls.build_view_name('detail')))

        if 'update' in cls.views_to_create:
            patterns.append(url(cls.build_url('update/(?P<pk>\d+)/$'), cls.update, name=cls.build_view_name('update')))

        if 'delete' in cls.views_to_create:
            patterns.append(url(cls.build_url('delete/(?P<pk>\d+)/$'), cls.delete, name=cls.build_view_name('delete')))

        if settings.DEBUG:
            patterns.append(url('^quickview/debug/$', cls.debug_view, name="quickview-debug"))

        return tuple(patterns)
