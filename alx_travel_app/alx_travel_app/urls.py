"""
URL configuration for alx_travel_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

def test_logging(request):
    """Test endpoint to verify logging is working"""
    payments_logger = logging.getLogger('payments')
    
    # Test different log levels
    payments_logger.debug("DEBUG test message")
    payments_logger.info("INFO test message")
    payments_logger.warning("WARNING test message")
    payments_logger.error("ERROR test message")
    payments_logger.critical("CRITICAL test message")
    
    # Test with extra context
    payments_logger.info("Payment test with context", extra={
        'transaction_id': 'test_123',
        'action': 'log_test',
        'user': 'test_user'
    })
    
    return HttpResponse("Log test completed. Check your log files.")

schema_view = get_schema_view(
   openapi.Info(
      title="ALX Travel App API",
      default_version='v1',
      description="API documentation for ALX Travel App",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/', include('listings.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

import logging

