from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from .models import Article, Subscription


@receiver(post_save, sender=Article)
def notify_new_article(sender, instance, created, **kwargs):
    if created:
        subscriptions = Subscription.objects.filter(category=instance.category)
        for sub in subscriptions:
            user = sub.user
            url = f"https://вашсайт.ru{reverse('article_detail', args=[instance.slug])}"
            send_mail(
                subject=f"Новая статья в категории {instance.category.name}",
                message=f"{instance.title}, {instance.summary} Читать: {url}", from_email = "noreply@вашсайт.ru", recipient_list = [user.email], )

    from django.contrib.auth.models import User

    @receiver(post_save, sender=User)
    def send_welcome_email(sender, instance, created, **kwargs):
        if created:
            send_mail(
                subject="Добро пожаловать на наш новостной портал!",
                message=f"Здравствуйте, {instance.username}! Спасибо за регистрацию на нашем сайте. ",
            from_email = "noreply@вашсайт.ru",
            recipient_list = [instance.email],
            )
