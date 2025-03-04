from django.contrib import admin
from .models import OrderPart, OrderCard

admin.site.register(OrderCard)
admin.site.register(OrderPart)
# Register your models here.
