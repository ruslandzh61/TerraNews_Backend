from django.dispatch import receiver
from django.db.models.signals import post_init
from ordinaryPython36.models import UserProfile, Channel, ChannelCategory
from ordinaryPython36.Supporting.services import CategoryService

@receiver(post_init, sender=UserProfile)
def setup_new_user_default_channels(sender, **kwargs):
    user = UserProfile.objects.get(id=kwargs.get('id'))
    print("test")
    for category in CategoryService().get_root_categories():
        print(category)
        channel = Channel.objects.create(user=user)
        ChannelCategory.objects.create(following_channel=channel,category=category)

