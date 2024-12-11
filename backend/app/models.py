from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username



class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100)
    client_nip = models.CharField(max_length=15)
    issue_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Dane systemowe
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey('UploadedFile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client_nip}"


class UploadedFile(models.Model):
    file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.file.name} - Processed: {self.processed}"
