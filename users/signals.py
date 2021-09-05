from django.db.models.signals import post_save
from django.dispatch import receiver
from tongozahome.models import *
from .models import User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    print('we came to after save')
    user = instance
    if created:
        print('new profile create')

        Profile.objects.create(user=user)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
