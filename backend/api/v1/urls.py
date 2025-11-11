from django.urls import path
from . import auth_views, views, product_views, cart_views, contact_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("import_shop/<int:shop_id>/", views.import_shop_data_api, name="import_shop_data_api_v1"),
    path("import_all_shops/", views.import_all_shops_data_api, name="import_all_shops_data_api_v1"),

    # URL для регистрации и аутентификации пользователя
    path("register/", auth_views.UserRegistrationAPIView.as_view(), name="user_registration_api_v1"),
    path("login/", auth_views.UserLoginAPIView.as_view(), name="token_obtain_pair_api_v1"), 
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_api_v1"),

    # URL для списка информации о товарах
    path("product-infos/", product_views.ProductInfoListView.as_view(), name="product_info_list_api_v1"),
    # URL для детальной информации о товаре
    path("products/<int:id>/", product_views.ProductDetailView.as_view(), name="product_detail_api_v1"),

    # URL для корзины
    path("cart/", cart_views.CartView.as_view(), name="cart_detail_api_v1"), # Получить/очистить корзину
    path("cart/add/", cart_views.CartItemAddView.as_view(), name="cart_item_add_api_v1"), # Добавить товар
    path("cart/item/<int:id>/", cart_views.CartItemView.as_view(), name="cart_item_api_v1"), # Обновить количество, удалить товар
    
    # URL для контактов
    path("contacts/", contact_views.ContactListView.as_view(), name="contact_list_api_v1"), # Список и создание
    path("contscts/<int:id>/", contact_views.ContactDetailView.as_view(), name="contact_detail_api_v1"), # Получить, обновить, удалить
]


