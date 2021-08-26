from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('users', views.UserViewSet)
router.register('update', views.AdminUserViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('admin/login/', views.AdminLoginView.as_view()),
    path('', include(router.urls)),
    path('analytics/report', views.AnalyticsView.as_view()),
    path('users/', views.UsersFilter.as_view()),
]
