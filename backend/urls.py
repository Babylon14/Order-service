from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="backend_index"),
    path("categories/", views.categories, name="backend_categories")
]


