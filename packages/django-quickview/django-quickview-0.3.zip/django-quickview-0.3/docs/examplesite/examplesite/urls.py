from django.conf.urls import patterns
from quickview import discover_views

urlpatterns = patterns('',
)

urlpatterns += discover_views()