from . import settings

def ga_tracking_id(request):
    is_super = request.user.is_authenticated() and request.user.is_superuser
    return dict(
        GA_TRACKING_ID=settings.GA_TRACKING_ID,
        GA_DOMAIN=settings.GA_DOMAIN,
        GA_USER_TRACKABLE=settings.GA_TRACK_SUPERUSER and is_super
    )
