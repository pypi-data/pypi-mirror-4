from . import settings

def ga_tracking_id(request):
    return dict(
        GA_TRACKING_ID=settings.GA_TRACKING_ID,
        GA_DOMAIN=settings.GA_DOMAIN,
    )
