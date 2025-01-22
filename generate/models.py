from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GeneratedText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GeneratedLegalDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    recipients = models.JSONField()
    description = models.TextField()
    agreements = models.JSONField()
    rights = models.JSONField(null=True, blank=True)
    resolution = models.TextField(null=True, blank=True)
    payment = models.TextField(null=True, blank=True)
    closing = models.DateTimeField()
    generated_content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
