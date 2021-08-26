import json
from io import BytesIO

from django.db.models import Count, Q
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from rest_framework import (
    viewsets,
    generics,
    permissions,
    mixins,
    decorators,
    response,
    status,
    filters,
    authentication,
    parsers
)
from rest_framework_simplejwt.views import TokenViewBase
from drf_yasg import openapi, utils as swagger_utils
from core import drf_permissions
from . import (
    serializers, models, utils, tasks
)
from django.core import serializers as core_serializers

from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime, timedelta


registration_token =  openapi.Parameter(
    'registration_token', openapi.IN_QUERY,
    description="registration_token",
    type=openapi.TYPE_STRING
)
secret_param = openapi.Parameter(
    'secret', openapi.IN_QUERY,
    description="secret",
    type=openapi.TYPE_STRING
)
user_id = openapi.Parameter(
    'user_id', openapi.IN_QUERY,
    description="user_id",
    type=openapi.TYPE_STRING
)
user_id_for_admin = openapi.Parameter(
    'user_id', openapi.IN_QUERY,
    description="user_id",
    type=openapi.TYPE_INTEGER,
    required=False
)
page = openapi.Parameter(
    'page', openapi.IN_QUERY,
    description="page",
    type=openapi.TYPE_INTEGER,
    required=False,
    default=1
)
per_page = openapi.Parameter(
    'per_page', openapi.IN_QUERY,
    description="per_page",
    type=openapi.TYPE_INTEGER,
    required=False,
    default=20
)
search = openapi.Parameter(
    'search', openapi.IN_QUERY,
    description="search",
    type=openapi.TYPE_STRING,
    required=False
)
order_by = openapi.Parameter(
    'order_by', openapi.IN_QUERY,
    description="order_by",
    type=openapi.TYPE_STRING,
    required=False,
    default='-requests_last_month'
)
order_direction = openapi.Parameter(
    'order_direction', openapi.IN_QUERY,
    description="asc or desc",
    type=openapi.TYPE_STRING,
    required=False,
    default='desc'
)

class LoginView(TokenViewBase):
    serializer_class = serializers.LoginSerializer
    queryset = models.User.objects.all()
    permission_classes = (permissions.AllowAny,)


class AdminLoginView(TokenViewBase):
    serializer_class = serializers.AdminLoginSerializer
    queryset = models.User.objects.all()
    permission_classes = (permissions.AllowAny,)


class RegisterView(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer
    queryset = models.User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return response.Response(
            serializers.UserSerializer(user).data
        )


class ResponseView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, **kwargs):
        return response.Response(
            'Approved',
            status=status.HTTP_200_OK
        )


class UsersFilter(generics.ListAPIView):
    permission_classes = (drf_permissions.IsOperator,)
    queryset = models.User.objects.all().order_by('-id')
    serializer_class = serializers.SafeUserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('id', 'created_at', 'role')
    pagination_class = serializers.StandardResultsSetPagination


class AdminUserViewSet(viewsets.GenericViewSet,mixins.UpdateModelMixin):
    queryset = models.User.objects.all()
    serializer_class = serializers.UpdateUserManuallySerializer

    def update(self, request, *args, **kwargs):
        if utils.is_valid_user(models.User, kwargs['pk'], request):

            return super().update(request, *args, **kwargs)
        else:
            return response.Response("Not Permitted", status=status.HTTP_403_FORBIDDEN)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    queryset = models.User.objects.all()
    serializer_class = serializers.SafeUserSerializer

    def list(self, request, *args, **kwargs):
        if utils.is_valid_user(models.User, None, request):
            return super().list(request, *args, **kwargs)
        else:
            return response.Response("Not Permitted", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id or drf_permissions.IsSuperAdmin:
            instance = self.get_object()
            super().perform_destroy(instance)
            return response.Response({'deleted': True}, status=status.HTTP_200_OK)
        return response.Response("Not Permitted", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        if utils.is_valid_user(models.User, kwargs['pk'], request):

            return super().update(request, *args, **kwargs)
        else:
            return response.Response("Not Permitted", status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if utils.is_valid_user(models.User, kwargs['pk'], request):

            return super().partial_update(request, *args, **kwargs)
        else:
            return response.Response("Not Permitted", status=status.HTTP_403_FORBIDDEN)

    @swagger_utils.swagger_auto_schema(
        method='get', manual_parameters=[secret_param, registration_token],
    )
    @decorators.action(
        methods=['get', ],
        serializer_class=serializers.UserSerializer,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def verify_phone(self, request, **kwargs):
        provided_secret = request.GET.get('secret', '')
        try:
            registration = request.GET.get('registration_token', '')
            obj = models.Registration.objects.get(key=registration)
        except Exception:
            return response.Response(
                "Record not found",
                status=status.HTTP_404_NOT_FOUND
            )
        if obj.code == provided_secret:
            obj.code_approved = True
            obj.save()
            return response.Response(
                'Code Approved',
                status=status.HTTP_200_OK
            )

        return response.Response(
            'Code is wrong or expired',
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_utils.swagger_auto_schema(
        method='get', manual_parameters=[secret_param, registration_token],
    )
    @decorators.action(
        methods=['get', ],
        serializer_class=serializers.UserSerializer,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def verify_email(self, request, **kwargs):
        secret = request.GET.get('secret', '')
        try:
            obj = models.User.objects.get(uuid=secret)
        except Exception:
            return response.Response(
                "Record not found",
                status=status.HTTP_404_NOT_FOUND
            )
        obj.is_email_verified = True
        obj.save()

        return redirect(settings.FRONTEND_APP_URL + '/create-property?s=' + str(obj.auth_token))
        # return redirect(settings.FRONTEND_APP_URL + '/email_verified?s=' + str(obj.auth_token))

    @swagger_utils.swagger_auto_schema(
        method='get', manual_parameters=[user_id_for_admin, page, per_page, search, order_by],
    )
    @decorators.action(
        methods=['get', ],
        # serializer_class=serializers.UserSerializer,
        detail=False,
        permission_classes=[
            permissions.IsAdminUser,
        ],
    )
    def get_users_list_with_requests_count(self, request, **kwargs):
        # today = datetime.now()
        # last_month = today.month - 1 if today.month > 1 else 12
        # last_month_year = today.year if today.month > last_month else today.year - 1
        # past_month_query = Q(created_at__year=last_month_year, created_at__month=last_month)
        # this_month = today.month - 1 if today.month > 1 else 12
        # this_month_year = today.year if today.month > this_month else today.year - 1
        # this_month_query = Q(created_at__year=this_month_year, created_at__month=this_month)
        month_ago = datetime.now()-timedelta(days=30)
        user_id = request.GET.get('user_id', None)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        search = request.GET.get('search', None)
        order_by = request.GET.get('order_by', '-requests_last_month')
        offset = (page - 1) * per_page
        offset_plus_limit = page * per_page
        query = models.User.objects.all()
        if user_id:
            query = models.User.objects.filter(pk=int(user_id))
        if search:
            query = query.filter(
                Q(name__contains=search) |
                Q(email__contains=search) |
                Q(phone_number__contains=str(search))
            )
        users = query.order_by(order_by)[offset:offset_plus_limit] \
            .annotate(requests_all=Count('user_requests')) \
            .annotate(requests_last_month=Count('user_requests', filter=Q(user_requests__created_at__gte=month_ago))) \
            .values('id', 'is_superuser', 'role', 'name', 'email', 'phone_number', 'created_at',
                    'requests_all', 'requests_last_month'
                    # 'requests_past_month', 'requests_this_month'
                    )
        users_count = models.User.objects.count()
        return response.Response(
            {'count': users_count, 'results': users},
            status=status.HTTP_200_OK
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.UpdateUserSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.IsSuperAdmin,
        ],
    )
    def update_all_users(self, request, **kwargs):
        serializer = self.get_serializer()
        serializer.write()
        return response.Response(
            'true'
        )

    @decorators.action(
            methods=['post', ],
            serializer_class=serializers.BulkUsersCreateSerializer,
            detail=False,
            permission_classes=[
                drf_permissions.IsSuperAdmin,
            ],
            parser_classes=[parsers.MultiPartParser,],
        )
    def upload_bulk_users(self, request, **kwargs):
        serializer = self.get_serializer()
        serializer.write(request)
        return response.Response(
            'true'
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.UserValidator,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def validate_user(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proceed = serializer.proceed(serializer.validated_data)
        return response.Response(
            serializers.RegistrationModelSerializer(proceed).data
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.RestoreValidator,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def generate_restore(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proceed = serializer.proceed(serializer.validated_data)
        return response.Response(
            { 'restore_key': proceed }
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.UpdateUserSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.IsSuperAdmin,
        ],
    )
    def update_all_users(self, request, **kwargs):
        serializer = self.get_serializer()
        serializer.write()
        return response.Response(
            'true'
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.ApproveRestoreValidator,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def approve_restore(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proceed = serializer.proceed(serializer.validated_data)
        return response.Response(
            'success'
        )
    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.SetPasswordSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.CORSPhoneVerified,
        ],
    )
    def set_new_password(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        return response.Response(
            serializers.UserSerializer(user).data
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.CreateUserManuallySerializer,
        detail=False,
        permission_classes=[
            drf_permissions.IsSuperAdmin,
        ],
    )
    def create_user(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create()
        return response.Response(
            serializers.SafeUserSerializer(user).data
        )

    @swagger_utils.swagger_auto_schema(
        method='get', manual_parameters=[secret_param],
    )
    @decorators.action(
        methods=['get', ],
        serializer_class=serializers.UserSerializer,
        detail=False,
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def resend_sms(self, request, **kwargs):
        provided_secret = request.GET.get('secret', '')
        if models.Registration.objects.filter(key=provided_secret).exists():
            registration = models.Registration.objects.get(key=provided_secret)
            tasks.send_very_sms.delay(registration.phone, registration.code)
            return response.Response(
                'ok'
            )
        return response.Response(
            'Wrong token',
            status=status.HTTP_400_BAD_REQUEST
        )

    @decorators.action(
        methods=['get', ],
        serializer_class=serializers.UserSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.CORSPhoneVerified,
        ],
    )
    def get_my_profile(self, request, **kwargs):
        return response.Response(
            serializers.UserSerializer(request.user).data
        )

    @decorators.action(
        methods=['post', ],
        serializer_class=serializers.UserDeviceSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.CORSPhoneVerified,
        ],
    )
    def add_device(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data
        )

    @decorators.action(
        methods=['post', ],
        detail=False,
        permission_classes=[
            drf_permissions.CORSPhoneVerified,
        ],
        serializer_class=serializers.UpdateUser,
    )
    def update_me(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data,  partial=True)
        serializer.is_valid(raise_exception=True)
        user = request.user
        u = serializer.save_update(user)
        return response.Response(serializers.UserSerializer(u).data)

    @decorators.action(
        methods=['patch', ],
        serializer_class=serializers.UserUpdateSerializer,
        detail=False,
        permission_classes=[
            drf_permissions.IsOperator,
        ],
        url_path='customers/update/(?P<pk>[^/.]+)'
    )
    def update_operator(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.set_new(instance)

        return response.Response(serializer.data)


class UserSubscriptionNotesViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin
):
    queryset = models.UserSubscriptionNotes.objects.all()
    serializer_class = serializers.UserSubscriptionNotes


class AnalyticsView(generics.GenericAPIView):
    serializer_class = serializers.FileSerializer
    permission_classes = (drf_permissions.IsSuperAdmin, )

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.data

        if query['type'] == 'users' and query['all_bool']:
            model = models.User
            queryset = model.objects.all()
        # elif query['type'] == 'suppliers' and query['all_bool']:
        #     model = processing_models.Supplier
        #     queryset = model.objects.all()
        else:
            if query['type'] == 'users':
                model = models.User
                queryset = models.User.objects.filter(
                    date_created__range=[query['date_from'], query['date_to']]).all()
            # elif query['type'] == 'suppliers':
            #     model = processing_models.Supplier
            #     queryset = model.objects.filter(
            #         date_created__range=[query['date_from'], query['date_to']]).all()

        _response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        _response['Content-Disposition'] = f'attachment; filename={datetime.now().strftime("%Y-%m-%d")}-{query["type"]}.xlsx'
        workbook = Workbook()

        worksheet = workbook.active
        worksheet.title = query['type']
        if query['type'] == 'users':
            users_data = serializers.SafeUserSerializer(queryset, many=True).data
        # if query['type'] == 'suppliers':
        #     suppliers_data = processing_serializers.SupplierSerializer(queryset, many=True).data

        columns = utils.columns(query['type'])
        row_num = 1

        for col_num, column_title in enumerate(columns, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = column_title

        rows = []
        if query['type'] == 'users':
            utils.generate_users(users_data, row_num, columns, rows, worksheet)
        if query['type'] == 'suppliers':
            utils.generate_suppliers(users_data, row_num, columns, rows, worksheet)

        workbook.save(_response)

        return _response


def set_date_object(addr):
    for field in ['action_start', 'action_end']:
        if (addr[field] is not None) and (addr[field] != ''):
            addr[field] = datetime.strptime(addr[field], '%Y-%m-%dT%H:%M:%S.%f')
    return addr
