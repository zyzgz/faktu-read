from django.contrib import admin
from .models import CustomUser, Invoice, UploadedFile


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client_nip', 'issue_date', 'due_date', 'total_amount', 'created_by', 'created_at', 'file')
    search_fields = ('invoice_number', 'client_nip')
    list_filter = ('issue_date', 'due_date', 'created_at')
    ordering = ('-issue_date',)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'processed')
    search_fields = ('file',)
    list_filter = ('uploaded_at', 'processed')
