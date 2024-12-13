from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Zwiększono max_digits dla wyższych kwot
    amount_due = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Opcjonalne pole na kwotę do zapłaty

    vendor_name = models.CharField(max_length=256, null=True, blank=True)
    vendor_address = models.CharField(max_length=512, null=True, blank=True)  # Zwiększono max_length dla dłuższych adresów
    vendor_tax_id = models.CharField(max_length=20, null=True, blank=True)  # Dostosowano długość do możliwych wariantów numerów NIP
    vendor_address_recipient = models.CharField(max_length=256, null=True, blank=True)  # Nowe pole

    customer_name = models.CharField(max_length=256, null=True, blank=True)
    customer_id = models.CharField(max_length=256, null=True, blank=True)  # Opcjonalne pole ID klienta
    customer_tax_id = models.CharField(max_length=20, null=True, blank=True)  # Dostosowano długość do możliwych wariantów numerów NIP
    customer_address = models.CharField(max_length=512, null=True, blank=True)

    billing_address = models.CharField(max_length=512, null=True, blank=True)  # Opcjonalny adres rozliczeniowy
    shipping_address = models.CharField(max_length=512, null=True, blank=True)  # Opcjonalny adres dostawy

    payment_term = models.CharField(max_length=100, null=True, blank=True)  # Nowe pole na termin płatności

    # Dane pozycji faktury
    items = models.JSONField(null=True, blank=True)  # Zastosowano JSONField do przechowywania pozycji

    # Dane systemowe
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey('UploadedFile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.vendor_tax_id}"


class UploadedFile(models.Model):
    file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.file.name} - Processed: {self.processed}"
