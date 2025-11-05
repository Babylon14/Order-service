from django.urls import path
from . import auth_views, views, product_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("import_shop/<int:shop_id>/", views.import_shop_data_api, name="import_shop_data_api_v1"),
    path("import_all_shops/", views.import_all_shops_data_api, name="import_all_shops_data_api_v1"),

    path("register/", auth_views.UserRegistrationAPIView.as_view(), name="user_registration_api_v1"),
    path("login/", auth_views.UserLoginAPIView.as_view(), name="token_obtain_pair_api_v1"), 
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_api_v1"),

    path("product-infos/", product_views.ProductInfoListView.as_view(), name="product_info_list_api_v1"),
    path("products/<int:id>/", product_views.ProductDetailView.as_view(), name="product_detail_api_v1"),
]


