from django.conf import settings

GA_TRACKING_ID = getattr(settings, 'GA_TRACKING_ID', None)
