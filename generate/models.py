from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

DOCUMENT_TYPE_CHOICES = [
    ('Cooperation Letter', 'Cooperation Letter'),
    ('Employment Agreement', 'Employment Agreement'),
    ('Request/Sales Letter', 'Request/Sales Letter'),
]

class GeneratedText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GeneratedLegalDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    document_type = models.CharField(max_length=50)
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

class Document(models.Model):
    document_title = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    comments_notes = models.TextField()
    expired_date = models.DateTimeField()
    document_number = models.CharField(max_length=20)
    envelope_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.document_type} - {self.document_title}"
