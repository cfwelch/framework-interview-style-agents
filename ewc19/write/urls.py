
from django.urls import re_path as url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^submit_logout', views.submit_logout, name='submit_logout'),
    url(r'^write', views.write, name='write'),
    url(r'^survey', views.survey, name='survey'),
    url(r'^intro', views.intro, name='intro'),
    url(r'^feedback', views.feedback, name='feedback'),
    url(r'^summary$', views.summary, name='summary'),
    url(r'^list_summary$', views.list_summary, name='list_summary'),
    url(r'^reset', views.reset, name='reset'),
    # url(r'^delall', views.delall, name='delall'),
    url(r'^ajax/send', views.send, name='send'),
]
