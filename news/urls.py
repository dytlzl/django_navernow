from django.urls import path
from . import views


urlpatterns = [
    path('', views.timeline, name='timeline'),
    path('search/<search_word>', views.search, name='search'),
    path('article/<pk>', views.article, name='article'),
]