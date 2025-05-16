from django.contrib import admin
from .models import Patient, Service, Visit, Payment, Doctor, Speciality

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'gender', 'address', 'telephone')
    search_fields = ('first_name', 'last_name')
    list_filter = ('gender',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('patient', 'total_price', 'paid_amount', 'payment_status')
    list_filter = ('payment_status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality')

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name',)
