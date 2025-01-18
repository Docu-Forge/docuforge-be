from django.db import models

# Create your models here.
from django.db import models

class DocumentRequest(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('Cooperation Letter', 'Cooperation Letter'),
        ('Employment Agreement', 'Employment Agreement'),
        ('Request/Sales Letter', 'Request/Sales Letter'),
    ]

    DOCUMENT_STATUS_CHOICES = [
        ('Sent for Signature', 'Sent for Signature'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    comments_notes = models.TextField()
    expired_date = models.DateTimeField()
    fullname = models.CharField(max_length=100)
    document_number = models.CharField(max_length=20)
    link_to_details = models.URLField()
    link_to_document = models.URLField()

    def __str__(self):
        return f"{self.document_type} - {self.fullname}"