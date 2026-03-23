from django.contrib import admin

from chat.models import *

# Register your models here.
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Group_Room)
admin.site.register(Group_message)
admin.site.register(GroupMember)