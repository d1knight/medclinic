
from django.contrib import admin
from django.urls import path, include
from admin_dashboard import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_dashboard/', include('admin_dashboard.urls')),
    path('', views.show_dashboard, name='show_dashboard')
]
