from django.conf.urls import url

from quickview.core_views import *
from quickview.exceptions import *
from quickview.model_views import *
from quickview.utils import *

def register_view(view):
    """

    """
    ViewRegistration.registered_views(view)
    return view


def discover_views(add_auth_pattern = True):
    """
    Discovers all quickviews in all installed apps and adds required urls. Also uses the ViewRegistration-class
    defined above to find information about views created by used the ModelQuickView-class as decorator.
    """
    ViewRegistration.scan_apps()

    urlpatterns = add_auth_pattern and [url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login-view'), \
                                        url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout-view')] or []

    for view in ViewRegistration.registered_views.values():
        urlpatterns += view.get_urls()

    return tuple(urlpatterns )