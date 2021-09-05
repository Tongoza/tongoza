from tongozahome.models import Profile, ProfileImage
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileUpdateImageForm


def retrieve_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()

    return profile


def set_profile_info(request):
    profile = retrieve_profile(request)
    profile_form = ProfileUpdateForm(request.POST, instance=profile)
    profile_form.save()


def set_user_info(request):
    profile = retrieve_profile(request)
    profile_form = UserUpdateForm(request.POST, instance=profile)
    profile_form.save()


def set_pic_info(request):
    profile = retrieve_profile(request)
    profile_form = ProfileUpdateImageForm(request.POST, request.FILES, instance=profile)
    profile_form.save()
