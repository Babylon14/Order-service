from django.urls import path
from . import auth_views, views, product_views, cart_views, contact_views, order_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [

    # URL для импорта данных конкретного магазина из YAML-файла
    path("import_shop/<int:shop_id>/", views.import_shop_data_api, name="import_shop_data_api_v1"),
    # URL для импорта всех данных из YAML-файлов
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
    path("cart/item/<int:id>/", cart_views.CartItemView.as_view(), name="cart_item_api_v1"), # Обновить количество
    
    # URL для контактов
    path("contacts/", contact_views.ContactListView.as_view(), name="contact_list_api_v1"), # Список и создание
    path("contacts/<int:id>/", contact_views.ContactDetailView.as_view(), name="contact_detail_api_v1"), # Получить, обновить, удалить
    
    # URL для подтверждения заказа
    path("confirm-order/", order_views.ConfirmOrderView.as_view(), name="order_confirm_api_v1"),

    # URL для истории заказов
    path("orders/", order_views.OrderHistoryView.as_view(), name="order_history_api_v1"),
    # URL для детальной информации о заказе
    path("orders/<int:id>/", order_views.OrderDetailView.as_view(), name="order_detail_api_v1"),

    # URL для подтверждения email
    path("confirm-email/<uuid:token>", auth_views.ConfirmEmailView.as_view(), name="email_confirmation_api_v1"),
]


