from tongozahome.models import Profile, Post
from friend.models import FriendList, FriendRequest
from django.contrib.flatpages.models import FlatPage
from django.contrib.sitemaps import Sitemap


class PostsSitemap(Sitemap):
    def items(self):
        return Post.objects.filter(active=True)


class ProfileSitemap(Sitemap):
    def items(self):
        return Profile.active.all()


class FlatPageSitemap(Sitemap):
    def items(self):
        return FlatPage.objects.all()


SITEMAPS = {'posts': PostsSitemap,
            'profiles': ProfileSitemap,
            'flatpages': FlatPageSitemap}
