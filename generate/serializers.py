from rest_framework import serializers

class RecipientSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)

class LegalDocumentSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    date = serializers.DateTimeField(required=True)
    recipients = serializers.ListSerializer(
        child=RecipientSerializer(),
        min_length=1
    )
    description = serializers.CharField(required=True)
    agreements = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
    rights = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default=list
    )
    resolution = serializers.CharField(required=False, allow_blank=True, default='')
    payment = serializers.CharField(required=False, allow_blank=True, default='')
    closing = serializers.DateTimeField(required=True)

class GenerateTextSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    response = serializers.CharField(read_only=True)
