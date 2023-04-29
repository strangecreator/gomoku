from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [ 
    path('make_connection', views.make_connection),
    path('get_connection', views.get_connection),
    path('make_move', views.make_move),
    path('get_state', views.get_state),
    path('resign', views.resign)
]
