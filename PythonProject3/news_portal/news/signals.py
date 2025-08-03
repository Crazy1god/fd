from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from .tasks import notify_new_article

@receiver(post_save, sender=Article)
def article_created(sender, instance, created, **kwargs):
    if created:
        notify_new_article.delay(instance.id)