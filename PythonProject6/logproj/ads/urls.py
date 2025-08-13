from django.urls import path
from .views import (
    AdListView, AdDetailView, AdCreateView, AdEditView, MyAdsView,
    ModerationQueueView, ModerationDecisionView, FavoriteToggleView,
    ComplaintCreateView, SendMessageView
)

app_name = "ads"

urlpatterns = [
    path("", AdListView.as_view(), name="list"),
    path("my/", MyAdsView.as_view(), name="my_ads"),
    path("new/", AdCreateView.as_view(), name="create"),
    path("<int:pk>/", AdDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", AdEditView.as_view(), name="edit"),
    path("<int:pk>/favorite/", FavoriteToggleView.as_view(), name="favorite"),
    path("<int:pk>/complaint/", ComplaintCreateView.as_view(), name="complaint"),
    path("<int:pk>/message/", SendMessageView.as_view(), name="message"),
    path("moderation/", ModerationQueueView.as_view(), name="moderation_queue"),
    path("moderation/<int:pk>/", ModerationDecisionView.as_view(), name="moderation_decision"),
]