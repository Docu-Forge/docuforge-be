from rest_framework import serializers
from .models import DocumentRequest

class DocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = [
            'id',
            'document_title',
            'document_type',
            'created_date',
            'comments_notes',
            'expired_date',
            'document_number',
            'envelope_id',
        ]