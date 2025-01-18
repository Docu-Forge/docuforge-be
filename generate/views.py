import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from openai import OpenAI
import logging
from rest_framework.views import APIView
from rest_framework import status

from .serializers import GenerateTextSerializer, LegalDocumentSerializer

env = os.environ

logger = logging.getLogger(__name__)

@api_view(['POST'])
def generate_text(request):
    serializer = GenerateTextSerializer(data=request.data)
    if serializer.is_valid():
        client = OpenAI(
            api_key=env.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": serializer.validated_data['prompt']},
            ],
            stream=False
        )
        
        return Response({
            'prompt': serializer.validated_data['prompt'],
            'response': response.choices[0].message.content
        })
    return Response(serializer.errors, status=400)

class GenerateLegalDocumentView(APIView):
    def format_recipients(self, recipients):
        return "\n".join([f"- {r['name']} ({r['role']})" for r in recipients])

    def format_list_field(self, items):
        return "\n".join([f"- {item}" for item in items])

    def create_prompt(self, data):
        prompt = f"""Generate a legal document with the following structure and information:

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
        
        prompt += "\n\nPlease format this into a professional legal document with proper legal language and structure."
        return prompt

    def post(self, request):
        try:
            serializer = LegalDocumentSerializer(data=request.data)
            if serializer.is_valid():
                # Log request (excluding sensitive data)
                logger.info(f"Generating legal document: {serializer.validated_data['title']}")
                
                client = OpenAI(
                    api_key=env.get('DEEPSEEK_API_KEY'),
                    base_url="https://api.deepseek.com"
                )
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a legal document assistant. Generate professional and legally sound documents based on the provided information."},
                        {"role": "user", "content": self.create_prompt(serializer.validated_data)}
                    ],
                    stream=False
                )
                
                generated_content = response.choices[0].message.content
                
                # Log success (excluding sensitive data)
                logger.info(f"Successfully generated document: {serializer.validated_data['title']}")
                
                return Response({
                    'title': serializer.validated_data['title'],
                    'generated_content': generated_content
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            return Response(
                {'error': 'Failed to generate document'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
