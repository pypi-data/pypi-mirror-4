from django.conf import settings

VISITOR_KEY = getattr(settings, 'VISITOR_KEY', 'visitor_key')
COOKIE_SAVED = getattr(settings, 'COOKIE_SAVED', 'cookie_saved')
COOKIE_VISITOR_KEY = getattr(settings, 'COOKIE_VISITOR_KEY', 'vk')
REQUEST_LOG_ID = getattr(settings, 'REQUEST_LOG_ID', 'request_log_id')
