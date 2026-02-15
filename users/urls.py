from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    JWTLoginView,
    UserRegistrationView,
    EmployeeListView,
    EmployeeAddView,
    EmployeeRemoveView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="auth-register"),
    path("login/", JWTLoginView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Управление сотрудниками (только владелец компании)
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("employees/add/", EmployeeAddView.as_view(), name="employee-add"),
    path("employees/<int:pk>/remove/", EmployeeRemoveView.as_view(), name="employee-remove"),
]
