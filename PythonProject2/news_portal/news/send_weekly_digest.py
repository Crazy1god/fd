from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.urls import reverse
from yourapp.models import Subscription, Article

class Command(BaseCommand):
    help = 'Send weekly digest to users'

    def handle(self, *args, **kwargs):
        week_ago = timezone.now() - timedelta(days=7)
        users = set(Subscription.objects.values_list('user', flat=True))
        for user_id in users:
            user_subs = Subscription.objects.filter(user_id=user_id)
            user = user_subs.first().user
            digest = ""
            for sub in user_subs:
                articles = Article.objects.filter(
                    category=sub.category, created_at__gte=week_ago
                )
                if articles.exists():
                    digest += f" Категория: {sub.category.name}"
                    for art in articles:
                        url = f"https://вашсайт.ru{reverse('article_detail', args=[art.slug])}"
                        digest += f"- {art.title} ({url})"
            if digest:
                send_mail(
                    subject="Новые статьи за неделю",
                    message=f"Здравствуйте, {user.username}! {digest}",
                    from_email="noreply@вашсайт.ru",
                    recipient_list=[user.email],
                )