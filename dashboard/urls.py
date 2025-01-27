from django.urls import path
from .views import DocumentList, AddDocument

app_name = 'dashboard'

urlpatterns = [
    path('get-documents', DocumentList.as_view(), name='get_documents'),
    path('add-document', AddDocument.as_view(), name='add_document'),
]
