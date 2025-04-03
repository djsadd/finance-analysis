from .views import index

from django.urls import include, path
urlpatterns = [
    path("translationsss/", index)
]