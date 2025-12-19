from pathlib import Path
from datetime import timedelta
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from dotenv import load_dotenv
import sys
import os


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["91.229.11.107", "127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = ["http://91.229.11.107", "http://localhost:3000"]

# Application definition
INSTALLED_APPS = [
    "jet",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",
    "social_django",
    "corsheaders",
    "debug_toolbar",
    "backend.apps.BackendConfig",
    "rest_framework_simplejwt",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "imagekit",
]
SITE_ID = 1 # для django.contrib.sites


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'orders.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'orders.wsgi.application'

# Если запущены тесты — используем SQLite
if "test" in sys.argv or os.environ.get("CI") == "true":
    print("!!! ИСПОЛЬЗУЕТСЯ SQLITE !!!")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    print("!!! ИСПОЛЬЗУЕТСЯ POSTGRESQL !!!")
    # В остальных случаях используем PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5434'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Где Django будет искать статику внутри приложений (например, админки)
STATIC_URL = "/static/"

# КУДА collectstatic будет копировать файлы
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# медиа-файлы (куда будут загружаться изображения пользователями)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Чтобы Django правильно строил ссылки на наш IP
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "http")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель пользователя
AUTH_USER_MODEL = "backend.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Добавляем JWT аутентификацию
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend", # Используем фильтры django-filter
        "rest_framework.filters.SearchFilter",               # Добавляем возможность поиска
        "rest_framework.filters.OrderingFilter",             # Добавляем возможность сортировки
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle", # Добавляем анонимные лимиты
        "rest_framework.throttling.UserRateThrottle", # Добавляем лимиты для пользователей
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "100/min",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Сервис заказов API",
    "DESCRIPTION": "это REST API сервис на базе Django и Django REST Framework"
                    "для управления заказами, товарами, корзиной и контактами пользователей."
                    "Сервис поддерживает работу с несколькими магазинами (поставщиками), "
                    "импорт данных из YAML-файлов, аутентификацию через JWT токены"
                    "и подтверждение email-адресов.",
    "VERSION": '1.0.0',
    "SERVE_INCLUDE_SCHEMA": False, # Включает генерацию схемы по маршруту /api/schema/
    # OTHER SETTINGS
}

# Настройки JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Настройки логирования
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",  # или INFO
    },
    "loggers": {
        "backend": {  # Имя вашего приложения
            "handlers": ["console"],
            "level": "DEBUG",  # или INFO
            "propagate": False,
        },
    },
}

# Настройки email подтверждения
# Используем консоль для отправки электронных писем
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  

# Другой вариант:
# Настройки SMTP для MailHog (обычно localhost)
EMAIL_HOST = "127.0.0.1"  # или 'localhost'
EMAIL_PORT = 1025         # Порт, на котором слушает MailHog
EMAIL_USE_TLS = False     # MailHog по умолчанию не использует TLS/SSL
EMAIL_USE_SSL = False     # MailHog по умолчанию не использует TLS/SSL
DEFAULT_FROM_EMAIL = "webmaster@localhost" 

# Настройка Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL") # Используем Redis в качестве брокера сообщений
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND") # Используем Redis в качестве брокера результатов

CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"


# --- Настройка Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

CACHES = {
    "default": { # Кэш по умолчанию (например, для session)
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1", # используем бд Redis 1 в качестве кэша (база 0 занята Celery)
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
            # Опция для обработки кэширования в транзакциях
            "IGNORE_EXCEPTIONS": True,
        },
        }
}

# --- Добавляем CLient ID и Secrets конкретных провайдеров ---
# OAuth2 - Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

# OAuth2 - GitHub
SOCIAL_AUTH_GITHUB_KEY = os.getenv("SOCIAL_AUTH_GITHUB_OAUTH2_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("SOCIAL_AUTH_GITHUB_OAUTH2_SECRET")

# --- Добавляем аутентификацию через социальные сети ---
AUTHENTICATION_BACKENDS = (
    # Дефолтная аутентификация (должна быть первой)
    'django.contrib.auth.backends.ModelBackend',
    # Добавляем аутентификацию через Google
    'social_core.backends.google.GoogleOAuth2',
    # Добавляем аутентификацию через GitHub
    'social_core.backends.github.GithubOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.user.user_details",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",

    # Кастомный пайплайн для генерации токена:
    "backend.auth_pipeline.generate_jwt_token",   
)

# URL фронтенда, на который нужно перенаправить после получения токенов
FRONTEND_SOCIAL_LOGIN_SUCCESS_URL = "http://127.0.0.1:3000/social-login-success"
# Перенаправляем на наше кастомное View для обработки токена
LOGIN_REDIRECT_URL = "/auth/complete-token/"

# URL, на который Social Auth делает *свой* редирект *после* завершения аутентификации
# Этот URL должен указывать на твой кастомный View
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = "http://127.0.0.1:3000/social-login-success"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/api/v1/auth/complete-token/"

# Разрешенные домены (Origin). В продакшене укажите домен вашего SPA!
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # "https://yourdomain.com",  # для продакшена
]

# Разрешаем кросс-доменные запросы
CORS_ALLOW_CREDENTIALS = True

# Если используем social-auth, добавьте эти настройки
SOCIAL_AUTH_JSONFIELD_ENABLED = True

# Отключаем автоматическую генерацию изображений ImageKit при сохранении модели
IMAGEKIT_CACHEFILE_NAMER = "imagekit.cachefiles.namers.source_name_hashed_dot"
IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = "imagekit.cachefiles.backends.Secure"
IMAGEKIT_SPEC_CACHEFILE_STORAGE = "imagekit.cachefiles.storage.Optimistic"

# ВАЖНО!!! Это гарантирует, что миниатюры не будут генерироваться синхронно при сохранении.
IMAGEKIT_PROCESS_DIRTY_FIELDS = False
IMAGEKIT_PROCESSOR_CACHE = "default"

SENTRY_DSN = os.getenv("SENTRY_DSN_BACKEND") # Указываем SENTRY_DSN для Django

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(), # Включаем интеграцию Django
            CeleryIntegration(), # Включаем интеграцию Celery
        ],
        # Настройка трассировки (APM)
        traces_sample_rate=1.0, # Записывать 100% транзакций (можно уменьшить в продакшене)
        # Дополнительные опции
        send_default_pii=True, # Отправлять личные данные (IP, заголовок, email аутентифицированного пользователя)
        environment="development", # Определяем окружение ('production' или 'staging')
    )


