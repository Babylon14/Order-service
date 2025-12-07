from django.urls import path
from . import (api_views, auth_views, product_views, cart_views, contact_views,
                order_views, social_auth_views, current_user_views)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # URL для импорта всех данных из YAML-файлов + Celery-задача
    path("start-import-all-shops/", api_views.StartImportAllShopsView.as_view(), name="start_import_all_shops_api_v1"),
    # URL для импорта данных конкретного магазина из YAML-файла + Celery-задача
    path("start-import-shop/<int:shop_id>/", api_views.StartImportShopView.as_view(), name="start_import_shop_api_v1"),
    # URL для статуса импорта
    path("import-status/<task_id>/", api_views.GetImportStatusView.as_view(), name="get_import_status_api_v1"),

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
    path("confirm-email/<uuid:token>/", auth_views.ConfirmEmailView.as_view(), name="email_confirmation_api_v1"),

    # URL для отправки подтверждения контакта по email
    path("send-contact-confirmation/", contact_views.SendConfirmationEmailView.as_view(), name="send_contact_confirmation_api_v1"),
    path("confirm-contact/<uuid:token>/", contact_views.ConfirmContactView.as_view(), name="confirm_contact_api_v1"),

    # URL для авторизации через социальные сети
    path("auth/complete-token/", social_auth_views.SocialAuthTokenRedirectView.as_view(), name="social_complete_token_api_v1"),
    path("users/me/", current_user_views.CurrentUserView.as_view(), name='current-user'),
]


