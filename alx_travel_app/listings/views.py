from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking, User
from rest_framework.response import Response
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Avg

# Create your views here.
class ListingViewSet(viewsets.ModelViewSet):
    # Ensuring CRUD operations for Listing model
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'price_per_night', 'bedrooms', 'bathrooms']
    search_fields = ['title', 'description', 'address', 'amenities']
    ordering_fields = ['price_per_night', 'created_at']

    def get_queryset(self):
        # filter the queryset to include related host and reviews for optimization
        queryset = Listing.objects.select_related('host').prefetch_related('reviews').all()
        
        # filter by avalability if start_date and end_date are provided in query params
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.exclude(
                bookings__start_date__lt=end_date,
                bookings__end_date__gt=start_date
            )
        
        # filter by price range if min_price and max_price are provided in query params
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            queryset = queryset.filter(price_per_night__gte=min_price, price_per_night__lte=max_price)
            queryset = queryset.annotate(average_rating=Avg('reviews__rating'))
            queryset = queryset.order_by('-average_rating')

        return queryset.distinct()

    def perform_create(self, serializer):
        # Automatically set the host to the logged-in user when creating a listing
        serializer.save(host=self.request.user)

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        # Retrieve bookings for a specific listing
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_booking(self, request, pk=None):
        # Create a new booking for a specific listing
        listing = self.get_object()
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(listing=listing, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        # Retrieve listings for the logged-in user
        user = request.user
        listings = Listing.objects.filter(host=user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    # Ensuring CRUD operations for Booking model
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['start_date', 'end_date', 'total_price']
    search_fields = ['listing__title', 'user__username']
    ordering_fields = ['start_date', 'end_date', 'total_price']

    def get_queryset(self):
        # users can only see their own bookings unless they are staff
        user = self.request.user
        queryset = Booking.objects.select_related('listing', 'user').all()
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # filter by date range if start_date and end_date are provided in query params
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(start_date__gte=start_date, end_date__lte=end_date)

        # filter by listing title if listing_title is provided in query params
        listing_title = self.request.query_params.get('listing_title')
        if listing_title:
            queryset = queryset.filter(listing__title__icontains=listing_title)
        return queryset.distinct()
    
    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user when creating a booking
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        # Retrieve bookings for the logged-in user
        user = request.user
        bookings = Booking.objects.filter(user=user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def host_bookings(self, request):
        # Retrieve bookings for listings owned by the logged-in host
        user = request.user
        listings = Listing.objects.filter(host=user)
        bookings = Booking.objects.filter(listing__in=listings)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        # Cancel a specific booking
        booking = self.get_object()
        if booking.user != request.user and not request.user.is_staff:
            return Response({'error': 'You do not have permission to cancel this booking.'}, status=403)
        booking.delete()
        return Response({'status': 'Booking cancelled'}, status=204)
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        # Reschedule a specific booking
        booking = self.get_object()
        if booking.user != request.user and not request.user.is_staff:
            return Response({'error': 'You do not have permission to reschedule this booking.'}, status=403)
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def confirm(self, request, pk=None):
        # Confirm a specific booking (for hosts)
        booking = self.get_object()
        if booking.listing.host != request.user and not request.user.is_staff:
            return Response({'error': 'You do not have permission to confirm this booking.'}, status=403)
        # Here you can add logic to mark the booking as confirmed
        return Response({'status': 'Booking confirmed'}, status=200)
