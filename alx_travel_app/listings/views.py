from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Listing, Booking, User, Payment
from rest_framework.response import Response
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Avg
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
from .chapa_service import ChapaService
from django.utils import timezone
import logging
import uuid

logger = logging.getLogger('payments')

# Create your views here.
class ListingViewSet(viewsets.ModelViewSet):
    # Ensuring CRUD operations for Listing model
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'price_per_night']
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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def initiate_payment(request, booking_id):
        """
        Initiate payment for a booking
        """
        logger.info("🎬 Payment initiation request received", extra={
            'booking_id': booking_id,
            'user': request.user.email,
            'action': 'initiate_payment_request'
        })
        
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Check if payment already exists
        if hasattr(booking, 'payment'):
            logger.warning("⚠️ Payment already exists for booking", extra={
                'booking_id': booking_id,
                'booking_reference': booking.reference,
                'action': 'payment_already_exists'
            })
            return Response({
                'error': 'Payment already initiated for this booking'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique transaction reference
        transaction_id = f"txn_{uuid.uuid4().hex[:10]}_{booking.reference}"
        
        # Prepare return URL
        return_url = request.build_absolute_uri(
            reverse('payment_success')
        ) + f"?booking={booking.reference}"
        
        # Log booking details
        logger.info("📋 Booking details for payment", extra={
            'booking_reference': booking.reference,
            'property': booking.property.title,
            'amount': float(booking.total_price),
            'check_in': booking.check_in.isoformat(),
            'check_out': booking.check_out.isoformat(),
            'transaction_id': transaction_id,
            'action': 'booking_details'
        })
        
        # Initialize Chapa service
        chapa = ChapaService()
        
        # Initiate payment
        payment_result = chapa.initiate_payment(
            amount=float(booking.total_price),
            email=request.user.email,
            first_name=request.user.first_name or 'Customer',
            last_name=request.user.last_name or 'User',
            tx_ref=transaction_id,
            return_url=return_url,
            custom_title=f"Payment for {booking.property.title}",
            custom_description=f"Booking reference: {booking.reference}"
        )
        
        if not payment_result['success']:
            logger.error("💥 Payment initiation failed in view", extra={
                'booking_id': booking_id,
                'transaction_id': transaction_id,
                'error': payment_result.get('message'),
                'action': 'payment_initiation_failed_view'
            })
            return Response({
                'error': payment_result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            transaction_id=transaction_id,
            amount=booking.total_price,
            status='pending',
            chapa_reference=transaction_id,
            initiation_response=payment_result.get('response_data')
        )
        
        logger.info("💰 Payment record created successfully", extra={
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'booking_reference': booking.reference,
            'status': 'pending',
            'action': 'payment_record_created'
        })
        
        return Response({
            'success': True,
            'checkout_url': payment_result['checkout_url'],
            'transaction_id': transaction_id,
            'message': 'Payment initiated successfully. Redirect to checkout URL.'
        })

    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def verify_payment(request):
        """
        Verify payment status
        """
        transaction_id = request.GET.get('transaction_id')
        booking_reference = request.GET.get('booking')
        
        if not transaction_id and not booking_reference:
            return Response({
                'error': 'Transaction ID or booking reference required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find payment
        if transaction_id:
            payment = get_object_or_404(Payment, transaction_id=transaction_id)
        else:
            booking = get_object_or_404(Booking, reference=booking_reference)
            payment = get_object_or_404(Payment, booking=booking)
        
        # Verify payment with Chapa
        chapa = ChapaService()
        verification_result = chapa.verify_payment(payment.transaction_id)
        
        if not verification_result['success']:
            return Response({
                'error': verification_result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update payment status
        chapa_status = verification_result['status']
        if chapa_status == 'success':
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.verification_response = verification_result.get('response_data')
            payment.save()
            
            # Update booking status
            payment.booking.status = 'confirmed'
            payment.booking.save()
            
            # Send confirmation email
            from .tasks import send_booking_confirmation
            send_booking_confirmation.delay(payment.booking.id)
            
            return Response({
                'success': True,
                'status': 'completed',
                'message': 'Payment verified successfully'
            })
        
        elif chapa_status in ['failed', 'cancelled']:
            payment.status = 'failed'
            payment.verification_response = verification_result.get('response_data')
            payment.save()
            
            return Response({
                'success': False,
                'status': 'failed',
                'message': 'Payment failed or was cancelled'
            })
        
        else:
            return Response({
                'success': False,
                'status': 'pending',
                'message': 'Payment is still pending'
            })


    @api_view(['POST'])
    def chapa_webhook(request):
        """
        Handle Chapa webhook for payment notifications
        """
        logger.info("📨 Chapa webhook received", extra={
            'remote_ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'action': 'webhook_received'
        })
        
        # Verify webhook signature (implement based on Chapa documentation)
        webhook_secret = settings.CHAPA_WEBHOOK_SECRET
        
        # Extract transaction ID from webhook data
        webhook_data = request.data
        transaction_id = webhook_data.get('tx_ref')
        event_type = webhook_data.get('event')
        
        logger.info("🔍 Processing webhook data", extra={
            'transaction_id': transaction_id,
            'event_type': event_type,
            'webhook_data': webhook_data,
            'action': 'webhook_processing'
        })
        
        if not transaction_id:
            logger.error("❌ Webhook missing transaction reference", extra={
                'webhook_data': webhook_data,
                'action': 'webhook_missing_tx_ref'
            })
            return Response({'error': 'No transaction reference'}, status=400)
        
        # Find and update payment
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            
            logger.info("🔍 Payment found for webhook", extra={
                'transaction_id': transaction_id,
                'payment_id': payment.id,
                'current_status': payment.status,
                'action': 'payment_found_webhook'
            })
            
            chapa = ChapaService()
            verification_result = chapa.verify_payment(transaction_id)
            
            if verification_result['success']:
                chapa_status = verification_result['status']
                
                if chapa_status == 'success':
                    payment.status = 'completed'
                    payment.paid_at = timezone.now()
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                    payment.verification_response = verification_result.get('response_data')
                    payment.save()
                    
                    logger.info("🎉 Payment completed via webhook", extra={
                        'transaction_id': transaction_id,
                        'payment_id': payment.id,
                        'booking_reference': payment.booking.reference,
                        'amount': float(payment.amount),
                        'action': 'payment_completed_webhook'
                    })
                    
                    # Send confirmation email
                    from .tasks import send_booking_confirmation
                    send_booking_confirmation.delay(payment.booking.id)
                    
                    logger.info("📧 Booking confirmation email triggered", extra={
                        'booking_id': payment.booking.id,
                        'action': 'email_triggered'
                    })
                
                elif chapa_status in ['failed', 'cancelled']:
                    payment.status = 'failed'
                    payment.verification_response = verification_result.get('response_data')
                    payment.save()
                    
                    logger.warning("⚠️ Payment failed via webhook", extra={
                        'transaction_id': transaction_id,
                        'status': chapa_status,
                        'action': 'payment_failed_webhook'
                    })
                
                else:
                    logger.info("⏳ Payment still pending via webhook", extra={
                        'transaction_id': transaction_id,
                        'status': chapa_status,
                        'action': 'payment_pending_webhook'
                    })
            
            else:
                logger.error("❌ Payment verification failed in webhook", extra={
                    'transaction_id': transaction_id,
                    'error': verification_result.get('message'),
                    'action': 'verification_failed_webhook'
                })
        
        except Payment.DoesNotExist:
            logger.error("❌ Payment not found for webhook", extra={
                'transaction_id': transaction_id,
                'action': 'payment_not_found_webhook'
            })
            return Response({'error': 'Payment not found'}, status=404)
        
        except Exception as e:
            logger.error("💥 Unexpected error in webhook processing", extra={
                'transaction_id': transaction_id,
                'error': str(e),
                'action': 'webhook_processing_error'
            })
            return Response({'error': 'Internal server error'}, status=500)
        
        logger.info("✅ Webhook processed successfully", extra={
            'transaction_id': transaction_id,
            'action': 'webhook_processed'
        })
        
        return Response({'status': 'webhook processed'})

    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def payment_success(request):
        """
        Success page after payment completion
        """
        booking_reference = request.GET.get('booking')
        transaction_id = request.GET.get('transaction_id')
        
        context = {
            'booking_reference': booking_reference,
            'transaction_id': transaction_id,
            'message': 'Payment completed successfully!'
        }
        
        return Response(context)