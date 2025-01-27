from django.conf import settings
from rest_framework.views import APIView
from .models import DocumentRequest
from .serializers import DocumentRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from generate.views import GenerateLegalDocumentView
from docusign_esign import ApiClient, EnvelopesApi
from django.http import FileResponse

class DocumentList(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        account_id = None
        user_info = GenerateLegalDocumentView.fetch_user_info(self= GenerateLegalDocumentView, token=token)
        accounts = user_info['accounts']
        for acc in accounts:
            if acc['is_default']:
                account_id = acc['account_id']
                break
        documents = DocumentRequest.objects.filter(account_id=account_id)
        serializer = DocumentRequestSerializer(documents, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Document fetched successfully",
            "contents": serializer.data
        }, status=status.HTTP_200_OK)

class GetRecipients(APIView):
    def get(self, request, envelope_id, account_id):
        user = request.user
        if not user:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        api_client = ApiClient()
        api_client.host = settings.DOCUSIGN['BASE_URL']
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        api_client.set_default_header("Authorization", f"Bearer {token}")

        envelope_api = EnvelopesApi(api_client)
        # Call the envelope recipients list method
        results = envelope_api.list_recipients(account_id=account_id, envelope_id=envelope_id)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Recipients fetched successfully",
            "contents": results.to_dict()
        }, status=status.HTTP_200_OK)
        

class GetDocumentLink(APIView):
    def get(self, request, envelope_id, account_id):
        user = request.user
        if not user:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized access"
            }, status=status.HTTP_401_UNAUTHORIZED)
        api_client = ApiClient()
        api_client.host = settings.DOCUSIGN['BASE_URL']
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        api_client.set_default_header("Authorization", f"Bearer {token}")

        envelope_api = EnvelopesApi(api_client)
        # Call the envelope recipients list method
        document_id = 1

        # Call the envelope get method to get the path of the temp file with the documents
        temp_file_path = envelope_api.get_document(
            account_id=account_id,
            document_id=document_id,
            envelope_id=envelope_id
        )
        results = envelope_api.list_documents(account_id=account_id, envelope_id=envelope_id).to_dict()
        print(results["envelope_documents"][0])
        doc_item = results["envelope_documents"][0]
        doc_name = doc_item["name"]
        has_pdf_suffix = doc_name[-4:].upper() == ".PDF"
        pdf_file = has_pdf_suffix
        # Add .pdf if it"s a content or summary doc and doesn"t already end in .pdf
        if (doc_item["type"] == "content" or doc_item["type"] == "summary") and not has_pdf_suffix:
            doc_name += ".pdf"
            pdf_file = True
        # Add .zip as appropriate
        if doc_item["type"] == "zip":
            doc_name += ".zip"

        # Return the file information
        if pdf_file:
            mimetype = "application/pdf"
        elif doc_item["type"] == "zip":
            mimetype = "application/zip"
        else:
            mimetype = "application/octet-stream"

        response = FileResponse(open(temp_file_path, "rb"), content_type=mimetype)
        response["Content-Disposition"] = f'attachment; filename="{doc_name}"'
        return response
        
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
        user = GenerateLegalDocumentView.fetch_user_info(user)
        document = DocumentRequest.objects.create(
            account_id=user,
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
