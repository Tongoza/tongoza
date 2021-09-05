from django.urls import path
from friend.views import (
    send_friend_request,
    view_friend_requests,
    accept_friend_request,
    view_friends,
    remove_friend,
    decline_friend_request,
    cancel_friend_request,
)


app_name = 'friend'

urlpatterns = [
    path('accept_friend_request/<friend_request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<friend_request_id>/', decline_friend_request, name='decline_friend_request'),
    path('friend_remove/', remove_friend, name='remove_friend'),
    path('friend_request/', send_friend_request, name='friend_request'),
    path('friend_request_cancel/', cancel_friend_request, name='friend_request_cancel'),
    path('friend_request/<slug>/', view_friend_requests, name='view_requests'),
    path('friends_list/<slug>/', view_friends, name='view_friends'),
]