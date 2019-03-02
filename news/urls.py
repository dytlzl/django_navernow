from django.urls import path
from . import views


urlpatterns = [
    path('', views.timeline, name='timeline'),
    path('article/<pk>', views.article, name='article'),
]