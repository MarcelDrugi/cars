from .base import *


DEBUG = False

ALLOWED_HOSTS = [env('BACKEND_HOST')]

CORS_ORIGIN_WHITELIST = (env('FRONTEND_HOST'))

# TrafficMiddleware only for production:
MIDDLEWARE.insert(0, 'car_rental.middleware.TrafficMiddleware')

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
