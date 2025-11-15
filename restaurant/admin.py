from django.contrib import admin
from .models import MenuItem, Category, Order, OrderItem, Payment, Table, OrderHistory, OrderHistoryItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.quantity * obj.price
    subtotal.short_description = 'Subtotal'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'date_edited']
    readonly_fields = ['date_edited']
    list_filter = ['payment_method', 'date_edited']

class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'is_occupied']
    list_filter = ['is_occupied']

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(OrderHistory)
admin.site.register(OrderHistoryItem)