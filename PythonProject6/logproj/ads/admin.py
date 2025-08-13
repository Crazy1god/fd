from django.contrib import admin
from .models import Ad, Category, City, AdImage, Favorite, Complaint, AdMessage

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "status", "created_at", "published_at", "expires_at", "views_count")
    list_filter = ("status", "category", "city", "created_at")
    search_fields = ("title", "description", "author__email")

admin.site.register([Category, City, AdImage, Favorite, Complaint, AdMessage])