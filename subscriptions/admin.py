from django.contrib import admin
from django.contrib import admin
from .models import SubscriptionPlan, BookPurchase


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(BookPurchase)
class BookPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'purchase_date')
    search_fields = ('user__username', 'book__title')
    list_filter = ('purchase_date',)
