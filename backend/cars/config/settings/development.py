from .base import *


DEBUG = True

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {},
    'JSON_EDITOR': True,
}

ALLOWED_HOSTS = []

CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:4200',
    'http://localhost:4200',
    'http://127.0.0.1:8000',
    'http://localhost:8000'
)


AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3-eu-west-1.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'aws_settings.storage_backend.MediaStorage'


STATIC_URL = '/static/'
MEDIA_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
MEDIA_ROOT = os.path.join(BASE_DIR, 'car_rental/media')
