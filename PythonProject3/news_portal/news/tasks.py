from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Article, Subscription

@shared_task
def notify_new_article(article_id):
    article = Article.objects.get(pk=article_id)
    subscriptions = Subscription.objects.filter(category=article.category)
    for sub in subscriptions:
        user = sub.user
        url = f"https://вашсайт.ru{reverse('article_detail', args=[article.slug])}"
        send_mail(
            subject=f"Новая статья в категории {article.category.name}",
            message=f"{article.title} {article.summary} Читать: {url}", from_email="noreply@вашсайт.ru", recipient_list=[user.email],)

@shared_task
def send_weekly_digest():
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
                    digest += f"- {art.title} ({url}) "
        if digest:
            send_mail(
                subject="Новые статьи за неделю",
                message=f"Здравствуйте, {user.username}! {digest}", from_email="noreply@вашсайт.ru", recipient_list=[user.email], )