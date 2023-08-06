from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'(?P<slug>[^/]+)/$', views.DetailView.as_view(),
        name='series_detail_view'),
)
