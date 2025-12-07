"""
URL configuration for orders project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.conf import settings
from backend.api import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("", views.index, name="index"),
    path("categories/", views.categories, name="categories"),

    # URL-маршрут для интерфейса админки
    path("jet/", include("jet.urls", "jet")),
    path("admin/", admin.site.urls),

    # URL-маршруты для схемы и отображения
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema")),

    # URL-маршруты для API
    path("api/", include("backend.api.urls")),

    # URL-маршрут для социальной авторизации
    path("auth/", include("social_django.urls", namespace="social")),
]

handler404 = "backend.api.views.page_not_found"
handler500 = "backend.api.views.server_error"

if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

