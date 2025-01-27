from .models import DocumentRequest
from rest_framework import serializers

class DocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = [
            'id',
            'document_type',
            'document_status',
            'created_date',
            'comments_notes',
            'expired_date',
            'fullname',
            'document_number',
            'link_to_details',
            'link_to_document',
        ]