from pathlib import Path
import os
from datetime import timedelta
from firebase_admin import initialize_app, credentials
from google.auth import load_credentials_from_file


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_j-tl4q7r1rxi3e+$bvvu&8_$edo$az^&r(vn1m%sltwqb5r&3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'base',
    'django_twilio',
    'fcm_django',
    'Inventory',
    'registry',

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
       'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# AUTHENTICATION_BACKENDS = ['base.api.backend.CustomUserModelBackend']

AUTH_USER_MODEL = 'base.CustomUser'

REST_FRAMEWORK = {

    # 'NON_FIELD_ERRORS_KEY':'error',
    'DEFAULT_AUTHENTICATION_CLASSES':(
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),

}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'systempro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'systempro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
       'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    #        'USER': 'postgres',
    #        'PASSWORD': 'rabee123',
    #        'HOST': 'localhost',
    #        'PORT': '5432',
       }
   }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT =  os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

}

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Replace with your preferred backend
# EMAIL_HOST = 'smtp.gmail.com' # Replace with your email host for gmail -> 'smtp.gmail.com'
# EMAIL_PORT = 587  # Replace with your email port
# EMAIL_USE_TLS = True  # Set to False if your email server doesn't use TLS
# EMAIL_HOST_USER = 'jacoubakizi81@gmail.com'  # Replace with your email username
# EMAIL_HOST_PASSWORD = 'eabqhwegdhezskam'  # Replace with your email password


class CustomFirebaseCredentials(credentials.ApplicationDefault):
    def __init__(self, account_file_path: str):
        super().__init__()
        self._account_file_path = account_file_path

    def _load_credential(self):
        if not self._g_credential:
            self._g_credential, self._project_id = load_credentials_from_file(
                self._account_file_path, scopes=credentials._scopes
            )

custom_credentials = CustomFirebaseCredentials('fcm_notification.json')
FIREBASE_MESSAGING_APP = initialize_app(custom_credentials, name='messaging')
FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": FIREBASE_MESSAGING_APP,
    "APP_VERBOSE_NAME":"what ever name",
    "ONE_DEVICE_PER_USER":False,
    "DELETE_INACTIVE_DEVICES":False,
}