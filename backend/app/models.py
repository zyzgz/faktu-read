from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username


class ExtractionOutput(models.Model):
    model_name = models.CharField(max_length=30)
    ocr_service = models.CharField(max_length=30)
    extracted_text = models.TextField(blank=True, null=True)
    api_version = models.CharField(max_length=30)
    pages = models.CharField(max_length=30)
