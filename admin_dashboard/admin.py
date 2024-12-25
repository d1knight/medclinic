from django.db import models
from django.contrib import admin
from .models import Patient, Service, Visit  # Импортируем модель из models.py

admin.site.register(Patient)  # Регистрируем модель в админке
admin.site.register(Service)
admin.site.register(Visit)