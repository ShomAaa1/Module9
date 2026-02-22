from django.urls import path
from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    CompanyJoinView,
    JoinRequestListView,
    JoinRequestApproveView,
    JoinRequestRejectView,
)

urlpatterns = [
    path("", CompanyListCreateView.as_view(), name="company-list-create"),
    path("<int:pk>/", CompanyDetailView.as_view(), name="company-detail"),
    path("<int:pk>/join/", CompanyJoinView.as_view(), name="company-join"),
    # Заявки на вступление (владелец компании)
    path("join-requests/", JoinRequestListView.as_view(), name="join-request-list"),
    path("join-requests/<int:pk>/approve/", JoinRequestApproveView.as_view(), name="join-request-approve"),
    path("join-requests/<int:pk>/reject/", JoinRequestRejectView.as_view(), name="join-request-reject"),
]
