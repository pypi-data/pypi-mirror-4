from django.conf import settings

GA_TRACKING_ID = getattr(settings, 'GA_TRACKING_ID')
GA_DOMAIN = getattr(settings, 'GA_DOMAIN')
GA_TRACK_SUPERUSER = getattr(settings, 'GA_TRACK_SUPERUSER', True)
