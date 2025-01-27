from rest_framework.views import APIView
from .models import DocumentRequest
from .serializers import DocumentRequestSerializer
from rest_framework.response import Response
from rest_framework import status

class DocumentList(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        documents = DocumentRequest.objects.all()
        serializer = DocumentRequestSerializer(documents, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Document fetched successfully",
            "contents": serializer.data
        }, status=status.HTTP_200_OK)

class AddDocument(APIView):
    def post(self, request):
        user = request.user
        if not user:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        document_title = request.data.get("document_title")
        document_type = request.data.get("document_type")
        comments_notes = request.data.get("comments_notes")
        expired_date = request.data.get("expired_date")
        document_number = request.data.get("document_number")
        envelope_id = request.data.get("envelope_id")
        document = DocumentRequest.objects.create(
            user=user,
            document_title=document_title,
            document_type=document_type,
            comments_notes=comments_notes,
            expired_date=expired_date,
            document_number=document_number,
            envelope_id=envelope_id
        )
        document.save()
        serializer = DocumentRequestSerializer(document)
        return Response({
            "status": status.HTTP_201_CREATED,
            "message": "Document added successfully",
            "contents": serializer.data
        }, status=status.HTTP_201_CREATED)        
