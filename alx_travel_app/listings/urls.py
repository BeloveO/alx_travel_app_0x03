from django.urls import path
from .views import ListingViewSet, BookingViewSet

urlpatterns = [
    # Define your URL patterns here if needed
    path('listings/', ListingViewSet.as_view({'get': 'list', 'post': 'create'}), name='listing-list'),
    path('listings/<int:pk>/', ListingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='listing-detail'),
    path('listings/<int:pk>/bookings/', ListingViewSet.as_view({'get': 'bookings', 'post': 'create_booking'}), name='listing-bookings'),
    path('bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='booking-list'),
    path('bookings/<int:pk>/', BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='booking-detail'),
    path('bookings/my/', BookingViewSet.as_view({'get': 'my_bookings'}), name='my-bookings'),
    path('bookings/host/', BookingViewSet.as_view({'get': 'host_bookings'}), name='host-bookings'),
]