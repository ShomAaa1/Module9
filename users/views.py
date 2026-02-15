from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    EmployeeSerializer,
    AddEmployeeSerializer,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Добавляем user в ответ JWT."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class JWTLoginView(TokenObtainPairView):
    """
    Вход по username и password. Возвращает access и refresh токены + данные пользователя.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Логин"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешный вход",
                examples={
                    "application/json": {
                        "access": "eyJ...",
                        "refresh": "eyJ...",
                        "user": {"id": 1, "username": "admin", "email": "admin@example.com"},
                    }
                },
            ),
            401: "Неверные учётные данные",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegistrationView(generics.CreateAPIView):
    """
    Регистрация нового пользователя. Доступно без авторизации.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Пользователь создан",
                examples={"application/json": {"id": 1, "username": "newuser", "email": "user@example.com"}},
            ),
            400: "Ошибка валидации",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


# ─── Управление сотрудниками (только владелец компании) ───


class EmployeeListView(generics.ListAPIView):
    """
    GET: список сотрудников компании. Доступно только владельцу.
    """
    serializer_class = EmployeeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "is_company_owner", False) and getattr(user, "company_id", None):
            return User.objects.filter(company_id=user.company_id)
        return User.objects.none()

    @swagger_auto_schema(
        responses={200: EmployeeSerializer(many=True), 403: "Только владелец компании"},
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_company_owner or not request.user.company_id:
            return Response(
                {"detail": "Только владелец компании может просматривать сотрудников."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().get(request, *args, **kwargs)


class EmployeeAddView(generics.GenericAPIView):
    """
    POST: добавить сотрудника в компанию по email. Доступно только владельцу.
    """
    queryset = User.objects.none()
    serializer_class = AddEmployeeSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=AddEmployeeSerializer,
        responses={
            200: EmployeeSerializer(),
            400: "Ошибка валидации",
            403: "Только владелец компании",
        },
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_company_owner or not request.user.company_id:
            return Response(
                {"detail": "Только владелец компании может добавлять сотрудников."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = User.objects.get(email=serializer.validated_data["email"])
        employee.company = request.user.company
        employee.save(update_fields=["company"])
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)


class EmployeeRemoveView(generics.GenericAPIView):
    """
    DELETE: удалить сотрудника из компании по id. Доступно только владельцу.
    Нельзя удалить самого себя (владельца).
    """
    queryset = User.objects.none()
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            204: "Сотрудник удалён из компании",
            403: "Только владелец / нельзя удалить себя",
            404: "Сотрудник не найден в компании",
        },
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_company_owner or not request.user.company_id:
            return Response(
                {"detail": "Только владелец компании может удалять сотрудников."},
                status=status.HTTP_403_FORBIDDEN,
            )
        employee_id = kwargs.get("pk")
        try:
            employee = User.objects.get(id=employee_id, company=request.user.company)
        except User.DoesNotExist:
            return Response(
                {"detail": "Сотрудник не найден в вашей компании."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if employee.id == request.user.id:
            return Response(
                {"detail": "Нельзя удалить владельца из компании."},
                status=status.HTTP_403_FORBIDDEN,
            )
        employee.company = None
        employee.save(update_fields=["company"])
        return Response(status=status.HTTP_204_NO_CONTENT)
