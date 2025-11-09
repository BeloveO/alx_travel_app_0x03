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
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def home_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALX Travel App - Deployment Successful</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ALX Travel App Deployment Successful!</h1>
            <p>Django application running.</p>
            <div>
                <a href="/admin/">Admin Panel</a>
                <a href="/swagger/" target="_blank">Swagger UI</a>
                <a href="/redoc/" target="_blank">ReDoc Documentation</a>
                <a href="/api/">API Endpoints</a>
            </div>
        </div>
    </body>
    </html>
    """)

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
)

def external_swagger(request):
    """Serve Swagger UI from external CDN"""
    swagger_ui_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALX Travel App - API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
        <style>
            html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
            *, *:before, *:after {{ box-sizing: inherit; }}
            body {{ margin:0; background: #fafafa; }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {{
                window.ui = SwaggerUIBundle({{
                    url: "{request.build_absolute_uri('/swagger.json')}",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                }});
            }};
        </script>
    </body>
    </html>
    """
    return HttpResponse(swagger_ui_html)
    

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('listings.urls')),
    path('swagger/', external_swagger),  # Use external Swagger UI
    path('swagger.json', schema_view.without_ui(cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

import logging

