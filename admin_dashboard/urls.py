from django.urls import path
from . import views

app_name = 'admin_dashboard'



urlpatterns = [
    path('', views.show_dashboard, name = 'show_dashboard'),
    path('patients', views.patient_list, name = 'patient_list'),
    path('patients/add/', views.patient_add, name='patient_add'),  # Путь для добавления пациента
    path('patients/<int:patient_id>/edit/', views.edit_patient, name='patient_edit'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='patient_delete'),
    path('services', views.service_list, name = 'service_list'),
    path('services/add/', views.service_add, name='service_add'),  # Путь для добавления услуги
    path('services/<int:service_id>/edit/', views.edit_service, name='service_edit'),
    path('services/<int:service_id>/delete/', views.delete_service, name='service_delete'),
    path('visits', views.visit_list, name = 'visit_list'),
    path('visits/add/', views.visit_add, name='visit_add'),
    path('visits/<int:visit_id>/print/', views.visit_print, name='visit_print'),
    path('visits/<int:visit_id>/payment/', views.visit_payment, name='visit_payment'),
]
