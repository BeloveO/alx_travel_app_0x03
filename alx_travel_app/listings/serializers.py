# Serializers for Listing and Booking models
from rest_framework import serializers
from .models import Listing, Booking, Review, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined']

# Serializer for the Listing model
class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer()
    host_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='host', write_only=True)
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'host', 'title', 'listing_image', 'description', 'description_image', 'property_type', 'amenities', 'address', 'price_per_night', 'created_at', 'reviews']
        read_only_fields = ['id', 'created_at', 'reviews']

#Serializer for the Booking model
class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    listing = ListingSerializer()
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), source='listing', write_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'listing', 'start_date', 'end_date', 'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']
