from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(User)
admin.site.register(House)
admin.site.register(Contact)
admin.site.register(HouseImage)
admin.site.register(Tenant)
admin.site.register(Income)
admin.site.register(Expense)

