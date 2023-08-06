import inspect
import json
from django.conf import settings
from django.conf.urls import url
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.models import model_to_dict
from quickview.utils import *


class QuickView(object):
    """

    """
    model_name = None
    app_label = None
    model = None
    authentication_required = False
    context = {}

    @classmethod
    def ajax_response(cls, request, data):
        """

        """
        return HttpResponse(json.dumps(data), content_type="application/json")

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
        context = {
            'debug': settings.DEBUG,
            'user': request.user
        }

        context.update(params)
        context.update(kwargs)
        context.update(cls.context)
        context.update(cls.get_context(request, *args, **kwargs))
        return context

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
    def _get_func_params(cls, func):
        """

        """
        params = []
        if is_py3():
            sig = inspect.signature(func)
            for param in sig.parameters.values():
                if param.name != 'request':
                    if sig.parameters[param.name].annotation == int:
                        params.append('(?P<%s>\\d+)' % param.name)
                    else:
                        params.append('(?P<%s>\\w+)' % param.name)
        else: # python 2.x
            for param in inspect.getargspec(func)[0][2:]:
                if param.endswith('_id'):
                    params.append('(?P<%s>\\d+)' % param)
                else:
                    params.append('(?P<%s>\\w+)' % param)

        return "/".join(params)

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
        for view in [v for v in dir(cls) if v.startswith('view_')]:
            v = getattr(cls, view)
            view_name = hasattr(v, 'view_name') and v.view_name or cls.build_view_name(v.__name__[5:])
            _url = cls.build_url(v.__name__[5:]) + "/$"
            views.append(url(_url, v, name=view_name))

        for view_name in cls._get_custom_ajax_views():
            _url = cls.build_url(view_name, prefix = "api") + '/$'
            views.append(url(_url, getattr(cls, 'ajax_view_%s' % view_name), name = cls.build_view_name(view_name, prefix = "api")))

        return tuple(views)

    @classmethod
    def _get_custom_ajax_views(cls):
        """

        """
        for view in [v for v in dir(cls) if v.startswith('ajax_view_')]:
            view_name = view[10:]
            if view_name in ('list', 'get', 'add', 'update', 'delete'):
                raise Exception("Invalid ajax name. '%s' is a reserved word in this context." % view_name)
            yield view_name

    @classmethod
    def build_template_path(cls, template_name):
        """

        """
        return "/".join(cls._get_parts(template_name))

    @classmethod
    def build_url(cls, view_name, prefix = None):
        """

        """
        return "^%s" % "/".join(cls._get_parts(view_name, prefix))

    @classmethod
    def build_view_name(cls, view_name, prefix = None):
        """

        """
        view_name = view_name.replace('_', '-')
        return "-".join(cls._get_parts(view_name, prefix))

    @classmethod
    def _get_parts(cls, last_part, prefix = None):
        parts = []
        if prefix:
            parts.append(prefix)

        if cls._app_label():
            parts.append(cls._app_label())

        if cls._model_name():
            parts.append(cls._model_name())

        if last_part:
            parts.append(last_part)

        return parts

    @classmethod
    def get_urls(cls):
        """

        """
        return cls._get_custom_views()