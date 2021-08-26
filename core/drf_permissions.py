from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class CORSIsAuthenticated(IsAuthenticated):

    def has_permission(self, request, view):
        return \
            (
                request.method in settings.SAFE_METHODS
                or request.user.is_authenticated
            )


class CORSPhoneVerified(IsAuthenticated):
    def has_permission(self, request, view):
        return \
            (
                request.method in settings.SAFE_METHODS
                or (
                        request.user.is_authenticated
                        and request.user.is_phone_verified
                )
            )


class CORSPhoneNotVerified(IsAuthenticated):
    def has_permission(self, request, view):
        return \
            (
                request.method in settings.SAFE_METHODS
                or (
                        request.user.is_authenticated
                        and not request.user.is_phone_verified
                        and request.user.role is not 'operator'
                )
            )


class IsSuperAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return \
            (
                request.method in settings.SAFE_METHODS
                or request.user.is_superuser

            )


class IsOperator(IsAuthenticated):
    def has_permission(self, request, view):
        return \
            (
                request.method in settings.SAFE_METHODS
                or (
                        request.user.is_staff
                        and request.user.role == 'operator'
                )
            )
