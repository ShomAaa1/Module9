from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Company, JoinRequest
from .serializers import CompanySerializer, CompanyCreateUpdateSerializer, JoinRequestSerializer
from .permissions import IsCompanyOwnerOrReadOnly


class CompanyListCreateView(generics.ListCreateAPIView):
    """
    GET: список компаний (все авторизованные).
    POST: создание компании (текущий пользователь становится владельцем).
    """
    permission_classes = (IsCompanyOwnerOrReadOnly,)
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CompanyCreateUpdateSerializer
        return CompanySerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["inn", "title"],
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING, description="ИНН (уникальный)"),
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Название компании"),
            },
        ),
        responses={201: CompanySerializer(), 400: "Ошибка валидации"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: информация о компании (все авторизованные).
    PUT/PATCH/DELETE: только владелец компании.
    """
    permission_classes = (IsCompanyOwnerOrReadOnly,)
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CompanyCreateUpdateSerializer
        return CompanySerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING),
                "title": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: CompanySerializer(), 403: "Только владелец", 404: "Не найдена"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING),
                "title": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: CompanySerializer(), 403: "Только владелец", 404: "Не найдена"},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CompanyJoinView(generics.GenericAPIView):
    """
    POST: подать заявку на вступление в компанию.
    Пользователь не должен состоять в компании и не должен быть владельцем.
    Заявку одобряет или отклоняет владелец компании.
    """
    queryset = Company.objects.all()
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=None,
        responses={
            201: JoinRequestSerializer(),
            400: "Пользователь уже в компании / заявка уже подана",
            404: "Компания не найдена",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.company_id is not None:
            return Response(
                {"detail": "Вы уже состоите в компании."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_company_owner:
            return Response(
                {"detail": "Владелец компании не может подать заявку в другую компанию."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        company = self.get_object()
        if JoinRequest.objects.filter(
            user=user, company=company, status=JoinRequest.Status.PENDING,
        ).exists():
            return Response(
                {"detail": "Вы уже подали заявку в эту компанию. Ожидайте решения владельца."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        join_request = JoinRequest.objects.create(user=user, company=company)
        return Response(
            JoinRequestSerializer(join_request).data,
            status=status.HTTP_201_CREATED,
        )


# ─── Заявки на вступление (только владелец компании) ───


class JoinRequestListView(generics.ListAPIView):
    """
    GET: список заявок на вступление в компанию владельца.
    Можно фильтровать по статусу: ?status=pending|approved|rejected
    """
    serializer_class = JoinRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if not user.is_company_owner or not user.company_id:
            return JoinRequest.objects.none()
        qs = JoinRequest.objects.filter(
            company_id=user.company_id,
        ).select_related("user", "company")
        status_filter = self.request.query_params.get("status")
        if status_filter in JoinRequest.Status.values:
            qs = qs.filter(status=status_filter)
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "status", openapi.IN_QUERY,
                description="Фильтр по статусу: pending, approved, rejected",
                type=openapi.TYPE_STRING,
                enum=["pending", "approved", "rejected"],
            ),
        ],
        responses={200: JoinRequestSerializer(many=True), 403: "Только владелец компании"},
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_company_owner or not request.user.company_id:
            return Response(
                {"detail": "Только владелец компании может просматривать заявки."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().get(request, *args, **kwargs)


class JoinRequestApproveView(generics.GenericAPIView):
    """
    POST: одобрить заявку на вступление. Пользователь прикрепляется к компании.
    """
    queryset = JoinRequest.objects.none()
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: JoinRequestSerializer(),
            400: "Заявка уже рассмотрена / пользователь уже в компании",
            403: "Только владелец компании",
            404: "Заявка не найдена",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_company_owner or not user.company_id:
            return Response(
                {"detail": "Только владелец компании может одобрять заявки."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            join_request = JoinRequest.objects.select_related("user").get(
                id=kwargs["pk"], company_id=user.company_id,
            )
        except JoinRequest.DoesNotExist:
            return Response(
                {"detail": "Заявка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if join_request.status != JoinRequest.Status.PENDING:
            return Response(
                {"detail": f"Заявка уже рассмотрена (статус: {join_request.get_status_display()})."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        applicant = join_request.user
        if applicant.company_id is not None:
            join_request.status = JoinRequest.Status.REJECTED
            join_request.reviewed_at = timezone.now()
            join_request.save(update_fields=["status", "reviewed_at"])
            return Response(
                {"detail": "Пользователь уже состоит в компании. Заявка автоматически отклонена."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        applicant.company_id = user.company_id
        applicant.save(update_fields=["company"])
        join_request.status = JoinRequest.Status.APPROVED
        join_request.reviewed_at = timezone.now()
        join_request.save(update_fields=["status", "reviewed_at"])
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)


class JoinRequestRejectView(generics.GenericAPIView):
    """
    POST: отклонить заявку на вступление.
    """
    queryset = JoinRequest.objects.none()
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: JoinRequestSerializer(),
            400: "Заявка уже рассмотрена",
            403: "Только владелец компании",
            404: "Заявка не найдена",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_company_owner or not user.company_id:
            return Response(
                {"detail": "Только владелец компании может отклонять заявки."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            join_request = JoinRequest.objects.get(
                id=kwargs["pk"], company_id=user.company_id,
            )
        except JoinRequest.DoesNotExist:
            return Response(
                {"detail": "Заявка не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if join_request.status != JoinRequest.Status.PENDING:
            return Response(
                {"detail": f"Заявка уже рассмотрена (статус: {join_request.get_status_display()})."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        join_request.status = JoinRequest.Status.REJECTED
        join_request.reviewed_at = timezone.now()
        join_request.save(update_fields=["status", "reviewed_at"])
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)
