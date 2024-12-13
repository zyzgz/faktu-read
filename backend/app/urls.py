from django.urls import path
from .views import (register_user, user_login, user_logout, check_login, upload_invoices,
                    generate_excel_report, get_invoices, list_reports, download_report, download_file)

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('check_login/', check_login, name='check_login'),
    path('upload-invoices/', upload_invoices, name='upload_invoice'),
    path('generate-excel-report/', generate_excel_report, name='generate_excel_report'),
    path('get-invoices/', get_invoices, name='get_invoices'),
    path('list-reports/', list_reports, name='list_reports'),
    path('download-report/<int:report_id>/', download_report, name='download_report'),
    path('download-file/<int:file_id>/', download_file, name='download_file'),
]
