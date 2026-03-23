from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(SalaryStructure)
admin.site.register(PaypalAccountInfo)
admin.site.register(Leave)
admin.site.register(Payroll)
admin.site.register(Payment)
admin.site.register(WebHookEvent)