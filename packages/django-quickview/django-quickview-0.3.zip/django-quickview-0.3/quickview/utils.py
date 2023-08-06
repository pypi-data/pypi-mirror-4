import sys
import inspect
from django.conf import settings
from django.db.models.fields import NOT_PROVIDED


class ViewRegistration(object):
    """
    This class will hold information about quickviews created when the user decorates a model using ModelQuickView.
    """
    registered_views = {}

    @classmethod
    def register(cls, view):
        """
        Registers a view so that discover_views will add it to the urlpatterns.
        """
        if not view.__name__ in cls.registered_views:
            cls.registered_views[view.__name__] = view

    @classmethod
    def unregister(cls, view):
        """
        Unregisters a view so that discover_views doesn't add it to the urlpatterns.
        """
        if view.__name__ in cls.registered_views:
            del cls.registered_views[view.__name__]

    @classmethod
    def scan_apps(cls):
        """
        Scans all installed apps for defined quickviews.
        """
        from quickview.core_views import QuickView
        from quickview.model_views import ModelQuickView

        apps = [ app for app in settings.INSTALLED_APPS if not "django" in app and not "quickview" in app]
        for app in apps:

            views = __import__('%s.views' % app, globals(), locals())
            for d in dir(views.views):
                m = getattr(views.views, d)
                if not inspect.isclass(m):
                    continue

                if issubclass(m, QuickView) and m is not QuickView and m is not ModelQuickView:
                    cls.register(m)


def get_field_names_from_model(model):
    """

    """
    result = {}
    field_defs = hasattr(model._meta, "_field_name_cache") and  model._meta._field_name_cache or model._meta._fields()
    for f in field_defs:
        result[f.name] = f.default != NOT_PROVIDED and f.default or None

    return result


def is_py3():
    """

    """
    return sys.version_info[0] == 3
