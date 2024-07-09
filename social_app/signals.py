from .models import Profile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Creates a profile for a newly created User instance.

    Returns:
        None
    """

    if created:
        Profile.objects.create(user=instance)
