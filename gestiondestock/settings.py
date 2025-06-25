import os

from pathlib import Path
import environ

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keepSS the secret key used in production secret!
SECRET_KEY = 'django-insecure-9wk9v#!qk$5j(-b3o@n1%ca@%*fiw9#62n@4t8w6()i)7z^0^0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed Hosts
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin',   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
    'widget_tweaks',
    'accounts',
    'carbone',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
]

ROOT_URLCONF = 'gestiondestock.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # <-- OK (important pour ton base_site.html)
        'APP_DIRS': True,  # <-- OK
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

WSGI_APPLICATION = 'gestiondestock.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JS, images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / 'static']  # ✔ pour trouver tes CSS

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py

# 1) Lecture du .env
import environ
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env') 
env = environ.Env()
env_file = BASE_DIR / '.env'
if env_file.exists():
    env.read_env(env_file)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# 2) DEBUG
DEBUG = env.bool("DEBUG", default=True)

# 3) Email (toujours SMTP Gmail)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

AUTH_USER_MODEL = 'inventory.CustomUser'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'gestiondestock0@gmail.com'
EMAIL_HOST_PASSWORD = 'pkbg aerr avpz rzvt'  # <= celui généré par Google !
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
AUTHENTICATION_BACKENDS = [
    'inventory.authentication.EmailOrSecondaryEmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]