from django.contrib import admin
from .models import Event, Ticket, Order, TicketCode
# Register your models here.

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'organizer')
    ordering = ('-event_date',)
    search_fields = ('title', 'location', 'organizer')


class TicketAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'price', 'quantity', 'sold', 'remaining_display')
    ordering = ('event', 'name')
    search_fields = ('event__title', 'name')
    list_filter = ('event',)
    readonly_fields = ('remaining_display',)

    def remaining_display(self, obj):
        return obj.remaining
    remaining_display.short_description = '剩餘票數'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticket', 'quantity', 'status', 'created_at', 'is_expired_display')
    ordering = ('-created_at',)
    search_fields = ('user__username', 'ticket__name', 'ticket__event__title')
    list_filter = ('status', 'created_at')

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = '是否已過期'
    is_expired_display.boolean = True


admin.site.register(Event, EventAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(TicketCode) 