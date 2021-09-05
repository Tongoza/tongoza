from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from friend.utils import get_friend_request_or_false
from tongozahome.models import Profile
from users.models import User
from friend.models import FriendRequest, FriendList
from django.contrib.auth.decorators import login_required


@login_required
def send_friend_request(request):
    sender = request.user
    print('sender_id', sender.id)
    payload = {}
    message = 'Friend request sent.'
    payload['message'] = message

    if request.method == 'POST':
        viewed_user_id = request.POST.get('receiver_user_id')
        print("viewed_user_id", viewed_user_id)
        if viewed_user_id:
            receiver = User.objects.get(pk=viewed_user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=sender, receiver=receiver)

                # find out if request is active
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception('You already sent them a friend request.')

                    friend_request = FriendRequest(sender=sender, receiver=receiver)
                    friend_request.save()
                    payload['response'] = message
                except Exception as e:
                    payload['response'] = str(e)

            except FriendRequest.DoesNotExist:
                # no existing friend request found
                friend_request = FriendRequest(sender=sender, receiver=receiver)
                friend_request.save()
                payload['response'] = message

            if payload['response'] is None:
                payload['response'] = 'Something went wrong. Try again.'
        else:
            payload['response'] = 'Unable to send a friend request.'
    else:
        payload['response'] = "You must be authenticated to send a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required
def view_friend_requests(request, *args, **kwargs):
    context = {}
    slug = kwargs.get('slug')
    print('viewed', slug)

    profile = Profile.objects.get(slug=slug)
    viewer = request.user
    profiles = []
    if profile.user == viewer:
        friend_requests = FriendRequest.objects.filter(receiver=viewer, is_active=True)
        context['friend_requests'] = friend_requests

        for friend_request_sender in friend_requests:
            # Get their respective profiles to load images
            profile = Profile.objects.get(user__id=friend_request_sender.sender.id)
            # print('profile found:', profile)
            profiles.append(profile)

            if get_friend_request_or_false(sender=friend_request_sender.sender, receiver=viewer):
                context['pending_friend_request_id'] = get_friend_request_or_false(
                    sender=friend_request_sender.sender, receiver=viewer).id
                print("pending", get_friend_request_or_false(sender=friend_request_sender.sender, receiver=viewer).id)

    else:
        HttpResponse("You trying to view another user's requests")
        return redirect('tongozahome:home')

    # print('profiles:', profiles)
    context['profiles'] = profiles
    return render(request, "friend/friend_requests.html", context)


@login_required
def accept_friend_request(request, *args, **kwargs):
    receiver = request.user
    payload = {}
    message = 'Friend request accepted.'
    if request.method == "GET":
        friend_request_id = kwargs.get('friend_request_id')
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm request
            if friend_request.receiver == receiver:
                if friend_request:
                    friend_request.accept()
                    payload['response'] = message
                else:
                    payload['response'] = "Something went wrong"
            else:
                payload['response'] = "Request is not yours to Accept"
        else:
            payload['response'] = 'Unable to accept Friend Request'
    else:
        payload['response'] = 'Login to continue'
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required
def view_friends(request, *args, **kwargs):
    viewer = request.user
    print('viewer', viewer)

    context = {}
    slug = kwargs.get('slug')
    viewed_profile = Profile.objects.get(slug=slug)
    print('viewed profile of friends', viewed_profile)

    profiles = []
    friend_list = FriendList.objects.get(user=viewed_profile.user)
    print('friend_list', friend_list)
    friends = friend_list.friends.all()
    print('friends', friends)

    # viewer_friend_list = FriendList.objects.get(user=)

    if friends:
        context['friends'] = friends
        for friend in friends:
            # get their individual profiles
            profile = Profile.objects.get(user__id=friend.id)
            profiles.append(profile)

    is_self = True
    is_friend = False
    if viewer != viewed_profile.user:
        is_self = False

    print('is_self', is_self)
    context['is_self'] = is_self
    context['is_friend'] = is_friend
    context['profiles'] = profiles
    context['viewed_profile'] = viewed_profile
    context['viewer'] = viewer

    return render(request, "friend/friends_list.html", context)


@login_required
def remove_friend(request, *args, **kwargs):
    remover = request.user
    payload = {}
    message = 'Successfully removed'

    if request.method == "POST":
        user_id = request.POST.get("receiver_user_id")
        print('id to be removed', user_id)
        if user_id:
            try:
                removee = User.objects.get(pk=user_id)

                friend_list = FriendList.objects.get(user=remover)
                print('remover friend list', friend_list)
                friend_list.unfriend(removee)
                print('remover friend list after', friend_list)

                payload['response'] = message
            except Exception as e:
                payload['response'] = f"Something went wrong:{str(e)}."
        else:
            payload['response'] = "There was an error. Unable to remove friend."
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required
def decline_friend_request(request, *args, **kwargs):
    decliner = request.user
    payload = {}
    if request.method == "GET":
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm request
            if friend_request.receiver == decliner:
                if friend_request:
                    friend_request.decline()
                    payload['response'] = "Friend Request Declined!"
                else:
                    payload['response'] = "Something went wrong!"
            else:
                payload['response'] = "Not your request to decline"
        else:
            payload['response'] = "Unable to declice friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required
def cancel_friend_request(request, *args, **kwargs):
    canceler = request.user
    print('canceler', canceler.id)
    payload = {}
    message = "Friend request cancelled"

    if request.method == "POST":
        user_id = request.POST.get("receiver_user_id")
        print('id to be removed', user_id)
        if user_id:
            try:
                receiver = User.objects.get(pk=user_id)
                print('receiver:', receiver)
                friend_requests = FriendRequest.objects.filter(sender=canceler, receiver=receiver, is_active=True)
                print('friend_requests', friend_requests)
                if len(friend_requests) > 1:
                    for request in friend_requests:
                        request.cancel()
                    payload['response'] = message
                else:
                    friend_requests.first().cancel()
                    payload['response'] = message
            except Exception as e:
                payload['response'] = "Nothing to cancel. Request does not exist."
        else:
            payload['response'] = "Unable to cancel request"

    return HttpResponse(json.dumps(payload), content_type="application/json")
