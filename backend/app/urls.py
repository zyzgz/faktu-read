from django.urls import path
from .views import register_user, user_login, user_logout, check_login, upload_invoices, generate_excel_report

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('check_login/', check_login, name='check_login'),
    path('upload-invoices/', upload_invoices, name='upload_invoice'),
    path('generate-excel-report/', generate_excel_report, name='generate_excel_report'),
]
