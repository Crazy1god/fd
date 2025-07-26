from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=get_user_model())
def add_to_common_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(group)