from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from decouple import config

# --- Entorno ------------------------------------------------------------
DEBUG = os.environ.get("DEBUG", "True") == "True"
if DEBUG:          # carga variables locales solo en desarrollo
    load_dotenv()

# --- Almacenamiento de archivos ----------------------------------------
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# --- Rutas base ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad ----------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", default="your secret key")
ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".herokuapp.com"]

# --- Aplicaciones instaladas -------------------------------------------
INSTALLED_APPS = [
    "storages",
    "admin_interface",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "kakureya.apps.KakureyaConfig",
]

# --- Middleware ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "CRUD.urls"

# --- Templates ----------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "CRUD.wsgi.application"

# --- Base de datos ------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),  # toma la URL desde el entorno
        conn_max_age=600,
    )
}
DATABASES["default"]["OPTIONS"] = {"client_encoding": "WIN1252"}

# --- AWS S3 -------------------------------------------------------------
AWS_ACCESS_KEY_ID        = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY    = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME  = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME       = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN     = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_FILE_OVERWRITE    = False     # evita sobrescritura
AWS_DEFAULT_ACL          = None
AWS_S3_ADDRESSING_STYLE  = "virtual"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
MEDIA_URL  = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_ROOT = ""                     # no se usa con S3

# --- Validación de contraseñas -----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ----------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "America/Bogota"
USE_I18N = True
USE_TZ   = True

# --- Archivos estáticos -------------------------------------------------
STATIC_URL = "/static/"

# carpeta local con los estáticos en desarrollo
STATICFILES_DIRS = [BASE_DIR / "kakureya" / "static"]

# carpeta generada por collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:     # compresión y hash en producción
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGIN_URL = "/signin"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email --------------------------------------------------------------
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = "smtp.gmail.com"
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get("EMAIL_USER", "tu_correo@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", "tu_contraseña_de_app")
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER

# --- Wompi --------------------------------------------------------------
WOMPI_PUBLIC_KEY     = os.getenv("WOMPI_PUBLIC_KEY", "")
WOMPI_INTEGRITY_SECRET = os.getenv("WOMPI_INTEGRITY_SECRET", "")
WOMPI_EVENTS_SECRET    = os.getenv("WOMPI_EVENTS_SECRET", "")