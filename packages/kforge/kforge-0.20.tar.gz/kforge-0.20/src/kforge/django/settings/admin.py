# Django settings for wui project admin site.

from main import *

TEMPLATE_DIRS = (
    '/usr/lib/python2.3/site-packages/django/conf/admin_templates',
    # Put strings here, like "/home/html/django_templates".
)
ROOT_URLCONF = 'wui.settings.urls.admin'
MIDDLEWARE_CLASSES = (
    'django.middleware.admin.AdminUserRequired',
    'django.middleware.common.CommonMiddleware',
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'
