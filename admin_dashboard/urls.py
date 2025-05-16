from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Главная страница панели администратора
    path('', views.show_dashboard, name='show_dashboard'),
    
    # Маршруты для пациентов
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_add, name='patient_add'),
    path('patients/<int:patient_id>/edit/', views.edit_patient, name='patient_edit'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='patient_delete'),
    path('patients/<int:patient_id>/history/', views.patient_history, name='patient_history'),
    
    # Маршруты для услуг
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.service_add, name='service_add'),
    path('services/<int:service_id>/edit/', views.edit_service, name='service_edit'),
    path('services/<int:service_id>/delete/', views.delete_service, name='service_delete'),
    
    # Маршруты для визитов
    path('visits/', views.visit_list, name='visit_list'),
    path('visits/add/', views.visit_add, name='visit_add'),
    path('visits/<int:visit_id>/payment/', views.visit_payment, name='visit_payment'),
    path('visits/<int:visit_id>/print/', views.visit_print, name='visit_print'),
]
