from django.db import models

DOCUMENT_TYPE_CHOICES = [
    ('Cooperation Letter', 'Cooperation Letter'),
    ('Employment Agreement', 'Employment Agreement'),
    ('Request/Sales Letter', 'Request/Sales Letter'),
]

class DocumentRequest(models.Model):
    account_id = models.CharField(max_length=100)
    document_title = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    comments_notes = models.TextField(default='') 
    expired_date = models.DateTimeField()
    document_number = models.CharField(max_length=20)
    envelope_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.document_type} - {self.document_title}"