from django.urls import path
from .views import ListingViewSet, BookingViewSet, PaymentViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payment', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]