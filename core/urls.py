from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from users import urls as auth_urls
from users import views
from django.conf import settings
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include(auth_urls)),
    path('', views.ResponseView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="Django Boilerplate API",
            default_version='v1',
            description="Django Boilerplate API",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        validators=['flex', 'ssv'],
        public=True,
    )
    urlpatterns += \
        [
            path(
                'redoc/', schema_view.with_ui('redoc', cache_timeout=None),
                name='schema-redoc'
            ),
            path('swagger/',
                 schema_view.with_ui('swagger', cache_timeout=None),
                 name='schema-swagger-ui'
                 ),
            path('docs/', include_docs_urls(title='My API title')),
        ]
