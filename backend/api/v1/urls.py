from django.urls import path
from . import auth_views, views


urlpatterns = [
    path("import_shop/<int:shop_id>/", views.import_shop_data_api, name="import_shop_data_api_v1"),
    path("import_all_shops/", views.import_all_shops_data_api, name="import_all_shops_data_api_v1"),
    path("register/", auth_views.UserRegistrationAPIView.as_view(), name="user_registration_api_v1"),
    path("login/", auth_views.UserLoginAPIView.as_view(), name="user_login_api_v1"), 
]


