from django.conf.urls import patterns, include, url

from .views import PersonList

urlpatterns = patterns('',
    url( r'^list$', PersonList.as_view(), name='thjodskra_list' ),
)
