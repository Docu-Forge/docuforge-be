from django.shortcuts import render
from rest_framework.views import APIView
from .models import DocumentRequest
from .serializers import DocumentRequestSerializer
from rest_framework.response import Response
from rest_framework import status
import uuid
from datetime import datetime

def generate_random_number():
    return str(uuid.uuid4().int)[:6]

DATA = [
    {
        "document_type": "Cooperation Letter",
        "document_status": "Completed",
        "comments_notes": "Initial contract",
        "expired_date": datetime(2024, 10, 1, 12, 0, 0),
        "fullname": "John Doe",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/123456",
        "linkto_document": "http://example.com/documents/123456",
    },
    {
        "document_type": "Employment Agreement",
        "document_status": "Sent for Signature",
        "comments_notes": "Non-disclosure agreement",
        "expired_date": datetime(2024, 10, 2, 14, 30, 0),
        "fullname": "Jane Smith",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/789012",
        "linkto_document": "http://example.com/documents/789012",
    },
    {
        "document_type": "Request/Sales Letter",
        "document_status": "Rejected",
        "comments_notes": "Invoice for services",
        "expired_date": datetime(2024, 10, 3, 9, 15, 0),
        "fullname": "Alice Johnson",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/345678",
        "linkto_document": "http://example.com/documents/345678",
    },
    {
        "document_type": "Cooperation Letter",
        "document_status": "Completed",
        "comments_notes": "Quarterly report",
        "expired_date": datetime(2024, 10, 4, 10, 0, 0),
        "fullname": "Bob Brown",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/901234",
        "linkto_document": "http://example.com/documents/901234",
    },
    {
        "document_type": "Employment Agreement",
        "document_status": "Sent for Signature",
        "comments_notes": "Internal memo",
        "expired_date": datetime(2024, 10, 5, 11, 30, 0),
        "fullname": "Charlie Davis",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/567890",
        "linkto_document": "http://example.com/documents/567890",
    },
    {
        "document_type": "Request/Sales Letter",
        "document_status": "Rejected",
        "comments_notes": "Project proposal",
        "expired_date": datetime(2024, 10, 6, 12, 45, 0),
        "fullname": "Diana Evans",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/234567",
        "linkto_document": "http://example.com/documents/234567",
    },
    {
        "document_type": "Cooperation Letter",
        "document_status": "Completed",
        "comments_notes": "Service agreement",
        "expired_date": datetime(2024, 10, 7, 14, 0, 0),
        "fullname": "Evan Foster",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/678901",
        "linkto_document": "http://example.com/documents/678901",
    },
    {
        "document_type": "Employment Agreement",
        "document_status": "Sent for Signature",
        "comments_notes": "Purchase order",
        "expired_date": datetime(2024, 10, 8, 15, 15, 0),
        "fullname": "Fiona Green",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/345678",
        "linkto_document": "http://example.com/documents/345678",
    },
    {
        "document_type": "Request/Sales Letter",
        "document_status": "Completed",
        "comments_notes": "Payment receipt",
        "expired_date": datetime(2024, 10, 9, 16, 30, 0),
        "fullname": "George Harris",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/789012",
        "linkto_document": "http://example.com/documents/789012",
    },
    {
        "document_type": "Cooperation Letter",
        "document_status": "Rejected",
        "comments_notes": "Meeting summary",
        "expired_date": datetime(2024, 10, 10, 17, 45, 0),
        "fullname": "Hannah Irving",
        "document_number": generate_random_number(),
        "linkto_details": "http://example.com/details/901234",
        "linkto_document": "http://example.com/documents/901234",
    }
]
class DocumentRequestList(APIView):
    def get(self, request):
        user = request.user
        print(user)
        if not user.is_superuser:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        document_requests = DocumentRequest.objects.all()
        serializer = DocumentRequestSerializer(document_requests, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "DocumentRequest fetched successfully",
            "contents": serializer.data
        }, status=status.HTTP_200_OK)
        
class AddDummyDocumentRequest(APIView):
    def post(self, request):
        for item in DATA:
            document_request = DocumentRequest.objects.create(
                document_type=item["document_type"],
                document_status=item["document_status"],
                comments_notes=item["comments_notes"],
                expired_date=item["expired_date"],
                fullname=item["fullname"],
                document_number=item["document_number"],
                link_to_details=item["linkto_details"],
                link_to_document=item["linkto_document"],
            )
            document_request.save()