from django.contrib import admin
from .models import CustomUser, Invoice, UploadedFile


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'invoice_date', 'due_date', 'total_amount',
        'vendor_name', 'vendor_tax_id', 'customer_name', 'customer_tax_id',
        'created_by', 'created_at', 'file'
    )
    search_fields = (
        'invoice_number', 'vendor_name', 'vendor_tax_id', 'customer_name', 'customer_tax_id'
    )
    list_filter = (
        'invoice_date', 'due_date', 'created_at'
    )
    ordering = ('-invoice_date',)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'processed')
    search_fields = ('file',)
    list_filter = ('uploaded_at', 'processed')
