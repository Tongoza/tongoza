import os

from tongozahome.models import *

timeout = 600  # 10 min


def tongoza(request):
    context = {}
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            print('userprofile:', profile)
            # dark_profile = DarkModeProfile.objects.get(user=request.user)

            context.update({
                'user_profile': profile,
                # 'user_dark_profile': dark_profile,
            })
        except Exception:
            pass

    return context
