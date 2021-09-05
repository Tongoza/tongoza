import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django.http import HttpResponseRedirect

from friend.friend_request_status import FriendRequestStatus
from friend.models import FriendList, FriendRequest
from users.forms import UserUpdateForm, ProfileUpdateForm, ProfileUpdateImageForm
from users.profile import set_pic_info, retrieve_profile
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, View, CreateView, UpdateView, DeleteView, FormView, TemplateView
from friend.utils import get_friend_request_or_false
from users.models import User
from .forms import PostForm
from .models import *

import logging

db_logger = logging.getLogger('db')

db_logger.info('info message')
db_logger.warning('warning message')


def home(request):
    return render(request, 'tongozahome/index.html')


class HomeView(ListView):
    model = Profile
    site_name = 'Ongoza'
    template_name = 'tongozahome/index.html'

    # paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        super(HomeView, self).get_context_data(**kwargs)

        context = {}

        try:
            active_profiles = Profile.active.all()
            print('active', active_profiles)

            active_posts = Post.objects.filter(active=True)
            print('active_posts', active_posts)

            public_posts = get_public_posts()
            print('public posts', public_posts)

            context['public_posts'] = public_posts

            context.update({
                'profiles': active_profiles,
                'posts': active_posts
            })
        except Exception as e:
            print('e', e)
            db_logger.exception(e)

        return context


@login_required()
def profileDetail(request, slug):
    print('in profile detail')
    context = {}

    viewed_profile = Profile.objects.get(slug=slug)
    print('viewed_profile:', viewed_profile)
    print('one seeing object:', request.user)

    public_posts = get_public_posts()
    print('public posts', public_posts)
    context['public_posts'] = public_posts
    all_posts = get_all_posts()
    context['all_posts'] = all_posts

    try:
        friend_list = FriendList.objects.get(user=viewed_profile.user)
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=viewed_profile.user)
        friend_list.save()

    friends = friend_list.friends.all()
    context['friends'] = friends

    viewed_user_account = viewed_profile.user
    is_self = True
    is_friend = False
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
    viewer = request.user
    if viewer != viewed_user_account:
        is_self = False
        if friends.filter(pk=viewer.id):
            is_friend = True
            print(viewer, 'and', viewed_user_account, 'are friends')
        else:
            is_friend = False
            # case 1 check if request has been sent from them to you
            if get_friend_request_or_false(sender=viewed_user_account, receiver=viewer):
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=viewed_user_account,
                                                                                   receiver=viewer).id

            # Case 2 - request has been sent from you to them
            elif get_friend_request_or_false(sender=viewer, receiver=viewed_user_account):
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # No request sent
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
    else:
        # Viewer is looking at their own profile
        print('Viewer is looking at their own profile')
        try:
            friend_requests = FriendRequest.objects.filter(receiver=viewer, is_active=True)
            context['friend_requests'] = friend_requests
        except:
            pass

    # caption = "False"

    # try:
    #     image_shown = viewed_profile.profileimage_set.get(in_display=True, public=True)
    #     print('image_shown:', image_shown.caption)
    #     if image_shown:
    #         if image_shown.caption:
    #             caption = "True"
    # except Exception:
    #     pass
    #
    # caption_json = json.dumps(caption)
    # print('caption is', caption_json)

    context['request_sent'] = request_sent
    context['is_friend'] = is_friend
    context['is_self'] = is_self
    context['object'] = viewed_profile
    # context['caption'] = caption_json

    return render(request, 'tongozahome/profile.html', context)


class ProfileDetailedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'tongozahome/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailedView, self).get_context_data()
        slug = self.kwargs['slug']
        print(slug)
        print(self.get_object())

        profile = get_object_or_404(Profile, slug=self.kwargs['slug'])
        print('Under view', profile)

        is_self = True
        is_friend = False
        user = self.request.user
        if user.is_authenticated and user != profile.user:
            is_self = False
        elif not user.is_authenticated:
            is_self = False

        # context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['BASE_URL'] = settings.BASE_URL

        return context


@login_required
def likeView(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    # post.likes.add(request.user)

    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('blog:postView', args=[str(slug)]))


class PostDetailedView(DetailView):
    model = Post
    template_name = 'tongozahome/postdetail.html'
    # template_name = 'blog/blog_single_test.html'
    query_pk_and_slug = False

    def get_context_data(self, **kwargs):
        context = super(PostDetailedView, self).get_context_data()

        post = get_object_or_404(Post, slug=self.kwargs['slug'])

        public_posts = get_public_posts().exclude(id=post.id)
        print('public posts', public_posts)
        context['public_posts'] = public_posts
        all_posts = get_all_posts()
        context['all_posts'] = all_posts

        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        context['liked'] = liked

        try:
            friend_list = FriendList.objects.get(user=post.author.user)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=post.author.user)
            friend_list.save()

        friends = friend_list.friends.all()
        context['friends'] = friends

        viewed_user_account = post.author.user
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        viewer = self.request.user
        if viewer != viewed_user_account:
            is_self = False
            if friends.filter(pk=viewer.id):
                is_friend = True
                print(viewer, 'and', viewed_user_account, 'are friends')
            else:
                is_friend = False
                # case 1 check if request has been sent from them to you
                if get_friend_request_or_false(sender=viewed_user_account, receiver=viewer):
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=viewed_user_account,
                                                                                       receiver=viewer).id

                # Case 2 - request has been sent from you to them
                elif get_friend_request_or_false(sender=viewer, receiver=viewed_user_account):
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                # No request sent
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        else:
            # Viewer is looking at their own profile
            print('Viewer is looking at their own profile')
            try:
                friend_requests = FriendRequest.objects.filter(receiver=viewer, is_active=True)
                context['friend_requests'] = friend_requests
            except:
                pass

        context['request_sent'] = request_sent
        context['is_friend'] = is_friend
        context['is_self'] = is_self

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # fields = ['product', 'title', 'content', 'image']
    template_name = 'tongozahome/modelforms/post_form.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse('tongozahome:postView', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Post Create',
        })
        return context

    def form_valid(self, form):
        # form.instance.seller = self.request.user
        obj = form.save(commit=False)
        profile = Profile.objects.get(user=self.request.user)
        obj.author = profile

        obj.save()
        return super(PostCreateView, self).form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    # fields = ['product', 'title', 'content', 'snippet', 'image']
    form_class = PostForm

    template_name = 'tongozahome/modelforms/post_form.html'

    # widgets = {
    #     'snippet': forms.Textarea(attrs={'class': 'form-control'})
    # }
    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Post Update',
        })
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'tongozahome/modelforms/post_confirm_delete.html'

    def get_success_url(self):
        post = Post.objects.get(slug=self.kwargs.get('slug'))

        return reverse('tongozahome:profile_images', kwargs={'slug': post.author.slug})

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Post Delete',
        })
        return context


def search_results(request):
    print('we came here')
    print(request)
    q = request.GET.get('q', '')
    # print('q', q)
    # context = {}
    # if request.method == "GET":
    #     search_query = request.GET.get("q", '')
    #     print('query:', search_query)
    #     if len(search_query) > 0:
    #         results = User.objects.filter(
    #             email__icontains=search_query).filter(
    #             username__icontains=search_query
    #         ).distinct()
    #         accounts = []
    #         for account in results:
    #             accounts.append((account, False))
    #         context['accounts'] = accounts

    return render(request, 'tongozahome/search_results.html')


@login_required
def show_profile_images(request, slug):
    profile = Profile.objects.get(slug=slug)

    profile_images = ProfileImage.objects.filter(profile=profile)
    posts = get_all_posts()
    print(profile_images)
    context = {
        'posts': posts,
        'object': profile,
        'profile_images': profile_images,
        'page_title': 'ImageList-' + str(profile)
    }

    return render(request, 'tongozahome/profileImagesList.html', context)


class ProfileImageCreateView(LoginRequiredMixin, CreateView):
    model = ProfileImage
    template_name = 'tongozahome/profileImageForm.html'
    form_class = ProfileUpdateImageForm

    # success_url = reverse_lazy("sellers:seller_products")

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        profile = Profile.objects.get(slug=self.kwargs.get('slug'))

        return reverse('tongozahome:profile_images', kwargs={'slug': profile.slug})

    def get_context_data(self, **kwargs):
        context = super(ProfileImageCreateView, self).get_context_data(**kwargs)

        profile = Profile.objects.filter(slug=self.kwargs.get('slug'))

        context.update({

            'page_title': 'Image Create',
            'profile': profile

        })
        return context

    def form_valid(self, form):
        print('In Add Image Form')
        # print(form)

        profile = Profile.objects.get(slug=self.kwargs.get('slug'))
        form.instance.profile = profile

        if form.is_valid():
            form = form.save(commit=False)
            print('valid form', form)
            if form.in_display:
                form.public = True

                current_saved_default = ProfileImage.displayed.filter(profile=profile, in_display=True,
                                                                      dark_mode_pic=False)
                print('current', current_saved_default)
                if current_saved_default.exists():
                    for image in current_saved_default:
                        image.in_display = False
                        image.save()

            current_saved_profile_pic = ProfileImage.displayed.filter(profile=profile, profile_pic=True)

            if form.profile_pic:

                print('current', current_saved_profile_pic)
                if current_saved_profile_pic.exists():
                    for image in current_saved_profile_pic:
                        image.profile_pic = False
                        image.save()

            if not form.profile_pic and not current_saved_profile_pic.exists():
                form.profile_pic = True
                form.save()

            form.save()
            return super().form_valid(form)


class ProfileImageUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfileImage
    template_name = 'tongozahome/profileImageForm.html'
    form_class = ProfileUpdateImageForm

    # field_class = ['image', 'in_display']

    # success_url = reverse_lazy("sellers:seller_products")

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        profile = Profile.objects.get(slug=self.get_object().profile.slug)

        return reverse('tongozahome:profile_images', kwargs={'slug': profile.slug})

    def get_context_data(self, **kwargs):
        context = super(ProfileImageUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Image Update',

        })
        return context

    def form_valid(self, form):
        print('In Update Image Validity')
        profile = Profile.objects.get(slug=self.get_object().profile.slug)

        # form.instance.profile = profile

        if form.is_valid():
            form = form.save(commit=False)
            # print('valid form', form)

            # check if it's a profile pic update

            obj = self.get_object().id
            print(obj)
            profile_pic_update = form.profile_pic
            print('pp checked:', profile_pic_update)
            in_display_update = form.in_display
            print('in d checked:', in_display_update)

            current_saved_profile_pic = ProfileImage.objects.filter(profile=profile, profile_pic=True,
                                                                    dark_mode_pic=False).exclude(id=obj)
            print('current saved profile pic', current_saved_profile_pic.exists())

            current_saved_in_display = ProfileImage.objects.filter(profile=profile, in_display=True,
                                                                   dark_mode_pic=False).exclude(id=obj)

            print('current saved in_display:', current_saved_in_display.exists())

            images = profile.profileimage_set.filter(public=True) \
                .exclude(id=self.get_object().id)
            print('images we can set in display or profile:', images)

            if len(images) >= 1:
                # if both the displayed pic and profile pic being updated or remain checked
                if profile_pic_update:
                    # case one: New profile pic
                    # check extisting profile pic
                    if current_saved_profile_pic:
                        print('disable currently stored image')
                        for image in current_saved_profile_pic:
                            image.profile_pic = False
                            image.save()

                # user updating only an image that is in display
                if in_display_update:
                    form.public = True
                    # case 1: check if there is existing in display and set it to false
                    if current_saved_in_display:
                        for image in current_saved_in_display:
                            image.in_display = False
                            image.save()

                # not in display, check other in display or set up one
                if not in_display_update:
                    print('we came to update in display false')
                    if not current_saved_in_display.exists():
                        print('yeah its true, it not there')
                        if current_saved_profile_pic.exists():
                            print('lets use the save profile')
                            for image in current_saved_profile_pic:
                                image.in_display = True
                                image.public = True
                                image.save()
                        else:
                            if images:
                                image = images[0]
                                image.in_display = True
                                image.public = True
                                image.save()

                if not profile_pic_update:
                    if not current_saved_profile_pic.exists():
                        if current_saved_in_display.exists():
                            for image in current_saved_in_display:
                                image.profile_pic = True
                                image.save()
                        else:
                            if images:
                                image = images[0]
                                image.profile_pic = True
                                image.save()

            else:
                print('we came to the remaining image')
                form.public = True
                form.profile_pic = True
                form.in_display = True

            form.save()
            return super().form_valid(form)


def delete_image(request, pk):
    print('using delete image function')

    image = ProfileImage.objects.get(id=pk)

    if image:
        if request.method == 'POST':
            print('image:', image)
            slug = image.profile.slug
            print('slug:', slug)

            if not image.in_display or image.profile_pic:
                image.delete()
                return redirect('tongozahome:profile_images', slug=slug)

            else:
                if image.in_display:
                    image.delete()

                    profile = Profile.objects.get(slug=slug)
                    current = profile.profileimage_set.all()
                    if current.exists():
                        print('we setting the new image on display')
                        new_image = current[0]
                        new_image.in_display = True
                        # delete old image
                        new_image.save()
                        return redirect('tongozahome:profile_images', slug=slug)
                    else:
                        profile = Profile.objects.get(slug=slug)
                        profile.save()
                        return redirect('tongozahome:profile_image_create', slug=slug)

                if image.profile_pic:
                    image.delete()

                    profile = Profile.objects.get(slug=slug)
                    current = profile.profileimage_set.all()
                    if current.exists():
                        print('we setting the new image for profile pic')
                        new_image = current[0]
                        new_image.profile_pic = True

                        # delete old image
                        new_image.save()
                        return redirect('tongozahome:profile_images', slug=slug)
                    else:
                        profile = Profile.objects.get(slug=slug)
                        profile.save()
                        return redirect('tongozahome:profile_image_create', slug=slug)

        else:
            context = {
                'image': image
            }
            return render(request, 'tongozahome/profile_image_delete.html', context)
    else:
        messages.warning(request, "An Error Occured: Clear Cache")
        return redirect('tongozahome:profile', slug=request.user.profile.slug)
