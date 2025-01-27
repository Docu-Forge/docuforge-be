from django.urls import path
from .views import DocumentRequestList, AddDummyDocumentRequest

app_name = 'dashboard'

urlpatterns = [
    path('get-document-requests', DocumentRequestList.as_view(), name='document_request_list'),
    path('add-dummy-document-request', AddDummyDocumentRequest.as_view(), name='add_dummy_document_request'),
]
