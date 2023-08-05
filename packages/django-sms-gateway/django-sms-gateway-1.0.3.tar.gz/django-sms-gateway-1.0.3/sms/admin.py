from django.contrib import admin
from sms.models import Gateway, Message, Reply

class GatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url')

class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_number', 
        'status', 
        'sender', 
        'local_send_time',
        'billed',
        'gateway',
        'gateway_charge',
        'billee'
    )
    list_filter = (
        'status',
        'billed',
        'gateway'
    )
    search_fields = (
        'recipient_number',
        'content',
    )
    raw_id_fields = ('sender', 'content_type')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ()
    
admin.site.register(Gateway, GatewayAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Reply, ReplyAdmin)
