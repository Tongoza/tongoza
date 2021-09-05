from .forms import UserUpdateForm, ProfileUpdateForm, ProfileUpdateImageForm
from .profile import set_pic_info, retrieve_profile
from django.contrib import messages
from django.shortcuts import reverse, render, redirect
from django.contrib.auth.decorators import login_required


@login_required()
def profileUpdate(request, slug, template_name="users/profileupdate.html"):
    if request.method == 'POST':
        print('we posting the infor')
        user_profile = retrieve_profile(request)
        postdata = request.POST.copy()
        # print(postdata)
        form_user = UserUpdateForm(postdata, instance=request.user)
        form_profile = ProfileUpdateForm(postdata, instance=user_profile)
        # form_pic = ProfileUpdateImageForm(request.POST or None, request.FILES or None, instance=request.user)

        if form_user.is_valid() and form_profile.is_valid():
            print('form is valid')
            form_user.save()
            form_profile.save()
            # form_pic.save()

            # set_pic_info(request)

            messages.success(request, f'Your account information has been updated')
            return redirect('tongozahome:profile', slug=slug)
        else:
            user_profile = retrieve_profile(request)
            form_user = UserUpdateForm(request.POST, instance=request.user)
            form_profile = ProfileUpdateForm(request.POST, instance=user_profile)
            # form_pic = ProfileUpdateImageForm(request.POST or None, request.FILES or None, instance=request.user)

            context = {
                'object': user_profile,
                'form_user': form_user,
                'form_profile': form_profile,
                # 'form_pic': form_pic,
            }
            return render(request, template_name, context)

    else:
        user_profile = retrieve_profile(request)
        form_user = UserUpdateForm(instance=request.user)
        form_profile = ProfileUpdateForm(instance=user_profile)
        # form_pic = ProfileUpdateImageForm(instance=user_profile)
        page_title = 'Update Information'
        is_self = True
        user = request.user
        if user != user_profile.user:
            is_self = False
        elif not user.is_authenticated:
            is_self = False
        context = {
            'object': user_profile,
            'form_user': form_user,
            'form_profile': form_profile,
            # 'form_pic': form_pic,
            'page_title': page_title,
            'is_self': is_self
        }
        return render(request, template_name, context)
