from django.db import models
from django.utils import timezone
from django.conf import settings
from utils.models import CreationModificationDateMixin


# Create your models here.

class FriendList(CreationModificationDateMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, removee):
        # initiate the action of unfriending
        remover_friends_list = self

        # Remove friend from remover friend list
        remover_friends_list.remove_friend(removee)

        # remove friend from removee friend list
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)
        friends_list.save()

    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(CreationModificationDateMixin):
    # sender - a person who initiates the friend request
    # receiver - a person receiving the friend request

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active = models.BooleanField(blank=True, null=False, default=True)

    def __str__(self):
        return '{}-{}'.format(self.sender, self.receiver)

    def accept(self):
        """
        update request on sender and receiver
        """

        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            receiver_friend_list.save()

        sender_friend_list = FriendList.objects.get(user=self.sender)
        if sender_friend_list:
            sender_friend_list.add_friend(self.receiver)
            self.is_active = False
            self.save()

    def decline(self):
        """
        Decline friend request
        set is active to false
        from receiver
        """

        self.is_active = False
        self.save()

    def cancel(self):
        """
        from the sender
        """
        self.is_active = False
        self.save()
