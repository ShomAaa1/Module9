from django.urls import path
from .views import StorageListCreateView, StorageDetailView

urlpatterns = [
    path("", StorageListCreateView.as_view(), name="storage-list-create"),
    path("<int:pk>/", StorageDetailView.as_view(), name="storage-detail"),
]
