from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
import logging
from .models import Ad,  Favorite,  Category, City
from .forms import AdForm, ModerationDecisionForm, ComplaintForm, MessageForm
from logproj.accounts.services import set_status, notify_new_message

logger = logging.getLogger("django")
sec_logger = logging.getLogger("django.security")

def is_moderator(user):
    return user.is_staff

class AdListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        qs = Ad.objects.filter(status=Ad.Status.PUBLISHED)
        q = request.GET.get("q")
        cat = request.GET.get("category")
        city = request.GET.get("city")
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        if city:
            qs = qs.filter(city_id=city)
        if price_min:
            qs = qs.filter(price__gte=price_min)
        if price_max:
            qs = qs.filter(price__lte=price_max)
        return render(request, "ads/ad_list.html", {"ads": qs, "categories": Category.objects.all(), "cities": City.objects.all()})

class AdDetailView(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk, status__in=[Ad.Status.PUBLISHED, Ad.Status.ARCHIVED])
        Ad.objects.filter(pk=ad.pk).update(views_count=models.F("views_count") + 1)
        return render(request, "ads/ad_detail.html", {"ad": ad, "message_form": MessageForm()})

class AdCreateView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "ads/ad_form.html", {"form": AdForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = AdForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "ads/ad_form.html", {"form": form}, status=400)
        ad = form.save(commit=False)
        ad.author = request.user
        ad.status = Ad.Status.DRAFT
        ad.save()
        if form.cleaned_data.get("submit_for_moderation"):
            set_status(ad, Ad.Status.PENDING)
        messages.success(request, "Объявление сохранено.")
        logger.info("Ad %s created by %s", ad.id, request.user.id)
        return redirect("ads:my_ads")

class MyAdsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "ads/ad_list.html", {"ads": Ad.objects.filter(author=request.user)})

class AdEditView(LoginRequiredMixin, View):
    def get_object(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk, author=request.user)
        if ad.status not in [Ad.Status.DRAFT, Ad.Status.REJECTED, Ad.Status.ARCHIVED]:
            messages.error(request, "Нельзя редактировать опубликованные/на модерации объявления.")
            raise Http404
        return ad

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = self.get_object(request, pk)
        form = AdForm(instance=ad)
        return render(request, "ads/ad_form.html", {"form": form, "ad": ad})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = self.get_object(request, pk)
        form = AdForm(request.POST, request.FILES, instance=ad)
        if not form.is_valid():
            return render(request, "ads/ad_form.html", {"form": form, "ad": ad}, status=400)
        ad = form.save()
        if form.cleaned_data.get("submit_for_moderation"):
            set_status(ad, Ad.Status.PENDING)
        messages.success(request, "Изменения сохранены.")
        logger.info("Ad %s edited by %s", ad.id, request.user.id)
        return redirect("ads:my_ads")

class ModerationQueueView(UserPassesTestMixin, View):
    def test_func(self):
        return is_moderator(self.request.user)

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "ads/moderation_list.html", {"ads": Ad.objects.filter(status=Ad.Status.PENDING)})

class ModerationDecisionView(UserPassesTestMixin, View):
    def test_func(self):
        return is_moderator(self.request.user)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk, status=Ad.Status.PENDING)
        return render(request, "ads/moderation_decision.html", {"ad": ad, "form": ModerationDecisionForm()})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk, status=Ad.Status.PENDING)
        form = ModerationDecisionForm(request.POST)
        if not form.is_valid():
            return render(request, "ads/moderation_decision.html", {"ad": ad, "form": form}, status=400)
        if form.cleaned_data.get("approve"):
            set_status(ad, Ad.Status.PUBLISHED)
            messages.success(request, "Объявление опубликовано.")
        else:
            comment = form.cleaned_data.get("comment", "")
            set_status(ad, Ad.Status.REJECTED, comment)
            messages.success(request, "Объявление отклонено.")
        return redirect("ads:moderation_queue")

class FavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk, status=Ad.Status.PUBLISHED)
        fav, created = Favorite.objects.get_or_create(user=request.user, ad=ad)
        if not created:
            fav.delete()
            messages.info(request, "Удалено из избранного.")
        else:
            messages.success(request, "Добавлено в избранное.")
        return redirect("ads:detail", pk=pk)

class ComplaintCreateView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk)
        form = ComplaintForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Ошибка валидации жалобы.")
            return redirect("ads:detail", pk=pk)
        complaint = form.save(commit=False)
        complaint.author = request.user
        complaint.ad = ad
        complaint.save()
        messages.success(request, "Жалоба отправлена.")
        logger.warning("Complaint submitted for ad %s by user %s", ad.id, request.user.id)
        return redirect("ads:detail", pk=pk)

class SendMessageView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        ad = get_object_or_404(Ad, pk=pk, status__in=[Ad.Status.PUBLISHED, Ad.Status.ARCHIVED])
        if ad.author_id == request.user.id:
            sec_logger.warning("Self-message attempt", extra={"ad": ad.id, "user": request.user.id})
            messages.error(request, "Нельзя писать самому себе.")
            return redirect("ads:detail", pk=pk)
        form = MessageForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Пустое сообщение.")
            return redirect("ads:detail", pk=pk)
        msg = form.save(commit=False)
        msg.ad = ad
        msg.sender = request.user
        msg.recipient = ad.author
        msg.save()
        notify_new_message(msg)
        messages.success(request, "Сообщение отправлено.")
        return redirect("ads:detail", pk=pk)