from django.urls import path
from .views import DocumentList, AddDocument, GetRecipients, GetDocumentLink

app_name = 'dashboard'

urlpatterns = [
    path('get-documents', DocumentList.as_view(), name='get_documents'),
    path('add-document', AddDocument.as_view(), name='add_document'),
    path('get-recipients/<str:envelope_id>/<str:account_id>', GetRecipients.as_view(), name='get_recipients'),
    path('get-document-link/<str:envelope_id>/<str:account_id>', GetDocumentLink.as_view(), name='get_document_link'),
]
