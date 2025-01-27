from django.urls import path
from . import views

app_name = 'generate'

urlpatterns = [
    path('legal-document/', views.GenerateLegalDocumentView.as_view(), name='generate_legal_document'),
]
