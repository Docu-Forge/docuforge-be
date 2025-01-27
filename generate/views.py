import os
import base64
from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework import status
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
from .serializers import LegalDocumentSerializer, GenerateTextSerializer
from .models import GeneratedLegalDocument
from django.conf import settings

env = os.environ


class GenerateLegalDocumentView(APIView):
    def format_recipients(self, recipients):
        return "\n".join([f"- {r['name']} ({r['email']})" for r in recipients])

    def format_list_field(self, items):
        return "\n".join([f"- {item}" for item in items])

    def create_prompt(self, data):
        prompt = f"""Generate a legal document based on the following data:

Title: {data['title']}
Date: {data['date']}

Recipients:
{self.format_recipients(data['recipients'])}

Description:
{data['description']}

Agreement Terms:
{self.format_list_field(data['agreements'])}"""

        # Add optional fields if present
        if data.get('rights'):
            prompt += f"\n\nRights and Obligations:\n{self.format_list_field(data['rights'])}"
        
        if data.get('resolution'):
            prompt += f"\n\nDispute Resolution:\n{data['resolution']}"
        
        if data.get('payment'):
            prompt += f"\n\nPayment Terms:\n{data['payment']}"
        
        prompt += f"\n\nClosing Date: {data['closing']}"
        
        prompt += "\n\nPlease format this into a professional legal document with proper legal language and structure. The response should be strictly in HTML with inline CSS only. No need for responsiveness or interactivity."
        return prompt

    def create_docusign_envelope(self, html_content, recipients):
        # Create the document model
        doc_b64 = base64.b64encode(bytes(html_content, "utf-8")).decode("ascii")
        document = Document(
            document_base64=doc_b64,
            name="Legal Document",
            file_extension="html",
            document_id="1"
        )

        # Create envelope definition
        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this legal document",
            documents=[document]
        )

        # Create signer models for all recipients
        signers = []
        for i, recipient in enumerate(recipients, start=1):
            signer = Signer(
                email=recipient['email'],
                name=recipient['name'],
                recipient_id=str(i),
                routing_order=str(i)
            )
            sign_here = SignHere(
                anchor_string="**signature_1**",
                anchor_units="pixels",
                anchor_y_offset="10",
                anchor_x_offset="20"
            )
            signer.tabs = Tabs(sign_here_tabs=[sign_here])
            signers.append(signer)

        # Add recipients to envelope
        recipients = Recipients(signers=signers)
        envelope_definition.recipients = recipients
        envelope_definition.status = "sent"

        return envelope_definition

    def fetch_user_info(self, token):
        from custom_auth.views import UserinfoView
        request = HttpRequest()
        request.method = 'GET'
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        userinfo_view = UserinfoView.as_view()
        response = userinfo_view(request)
        
        if response.status_code == status.HTTP_200_OK:
            return response.data['contents']
        else:
            raise Exception("Failed to retrieve user information")

    def retrieve_access_token(self, token):
        api_client = ApiClient()
        api_client.host = settings.DOCUSIGN['AUTH_SERVER']
        api_client.set_default_header("Authorization", f"Bearer {token}")
        return api_client

    def create_and_send_envelope(self, api_client, account_id, validated_content, recipients):
        envelope_definition = self.create_docusign_envelope(validated_content, recipients)
        # print(envelope_definition)
        envelopes_api = EnvelopesApi(api_client)
        # print(envelopes_api)
        result = envelopes_api.create_envelope(account_id=account_id, envelope_definition=envelope_definition)
        # print(result)
        return result

    def post(self, request):
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            
            account_id = None

            # Retrieve user information using the token
            try:
                user_info = self.fetch_user_info(token)
                user_id = user_info['sub']
                accounts = user_info['accounts']
                for acc in accounts:
                    if acc['is_default']:
                        account_id = acc['account_id']
                        break
            except Exception as e:
                return Response({'error': 'Failed to retrieve user information'}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = LegalDocumentSerializer(data=request.data)
            if serializer.is_valid():
                # Log request (excluding sensitive data)
                
                client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a legal document assistant. Generate professional and legally sound documents based on the provided information. The response should be in english. You're allowed to re-phrase the data given to you to sound more lgal.The response should be strictly in HTML with inline CSS only. No need for responsiveness or interactivity."},
                        {"role": "user", "content": self.create_prompt(serializer.validated_data)}
                    ],
                    stream=False
                )
                
                generated_content = response.choices[0].message.content
                validated_content = generated_content.replace("```html", "").replace("```", "").strip()

                # Create DocuSign API client
                api_client = ApiClient()
                api_client.host = settings.DOCUSIGN['BASE_URL']
                api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {token}")

                # Create and send envelope
                try:
                    result = self.create_and_send_envelope(api_client, account_id, validated_content, serializer.validated_data['recipients'])
                    print(result)
                except Exception as e:
                    print(f"Error creating envelope: {str(e)}")
                    return Response({'error': 'Failed to create envelope'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Save the generated document to the database
                # self.save_generated_document(user_id, serializer, validated_content)

                return Response({
                    'title': serializer.validated_data['title'],
                    'generated_content': validated_content,
                    'envelope_id': result.envelope_id
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': 'Failed to generate document'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
