import logging

from django import template

from friend.models import FriendRequest

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def notification_item_count(request):
    # if request.cart_id:
    #     qs = Order.objects.filter(cart_id=request.cart_id, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()

    if request.cart:
        return request.cart.items.count()
    return 0


@register.filter
def friend_request_count(request):
    friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)

    if friend_requests:
        return friend_requests.count()
    return 0


@register.filter
def cart_item_total(request):
    # if request.cart_id:
    #     qs = Order.objects.filter(cart_id=request.cart_id, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()

    if request.cart:
        return request.cart.get_total()
    return 0


@register.filter
def wish_list_count(request):
    # if request.cart_id:
    #     qs = Order.objects.filter(cart_id=request.cart_id, ordered=False)
    #     if qs.exists():
    #         return qs[0].items.count()

    if request.user:
        from utils import context_processors
        try:
            wishlist = context_processors.me2u(request)['wish_list']
            # print(wishlist)
            return wishlist.count()
        except Exception:
            return 0
    return 0
