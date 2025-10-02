# ALX Travel App

A comprehensive Django-based travel accommodation platform that allows users to discover, book, and manage property listings with real-time messaging and booking capabilities.

## 🌟 Features

### Core Functionality

- **Property Listings**: Hosts can create and manage property listings with detailed information
- **Booking System**: Secure booking system with date availability checking
- **Real-time Messaging**: Threaded conversations between hosts and guests
- **User Reviews**: Rating and review system for completed bookings
- **Notifications**: Real-time notifications for new messages and booking updates

### Advanced Features

- **Search & Filtering**: Advanced search with multiple filter options
- **RESTful API**: Complete API for mobile and third-party integrations

## 🏗️ Architecture

### Tech Stack

- **Backend**: Django 4.x, Django REST Framework
- **Database**: PostgreSQL (recommended) / SQLite
- **Authentication**: Django Authentication System
- **API**: RESTful API with DRF ViewSets
- **Real-time**: Django Channels (ready for WebSocket integration)

### Models Overview

- **User**: Extended Django User model with travel-specific features
- **Listing**: Property listings with amenities, pricing, and availability
- **Booking**: Reservation system with status tracking
- **Review**: Rating and review system

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Django 4.x
- Django REST Framework

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd alx_travel_app_0x01
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your database and secret key
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create superuser**

```bash
python manage.py createsuperuser
```

7. **Run development server**

```bash
python manage.py runserver
```

## 📚 API Documentation

### Authentication

The API uses session authentication for web interface and token authentication for mobile clients.

### Key Endpoints

#### Listings

- `GET /api/listings/` - Browse all listings
- `POST /api/listings/` - Create new listing (hosts only)
- `GET /api/listings/{id}/` - Get listing details
- `PUT /api/listings/{id}/` - Update listing (host only)
- `DELETE /api/listings/{id}/` - Delete listing (host only)

#### Bookings

- `GET /api/bookings/` - User's bookings (as guest or host)
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Booking details
- `PUT /api/bookings/{id}/` - Update booking status
- `DELETE /api/bookings/{id}/` - Cancel booking

### Example API Usage

#### Create a Listing

```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your-token>" \
  -d '{
    "title": "Cozy Mountain Cabin",
    "description": "Beautiful cabin with mountain views",
    "property_type": "cabin",
    "address": "123 Mountain Road",
    "city": "Aspen",
    "state": "Colorado",
    "country": "USA",
    "price_per_night": 150.00,
    "max_guests": 4,
    "bedrooms": 2,
    "bathrooms": 1,
    "amenities": [ "wifi", "fireplace", "kitchen"]
  }'
```

### Make a Booking

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your-token>" \
  -d '{
    "listing": 1,
    "check_in": "2024-03-15",
    "check_out": "2024-03-20",
    "total_guests": 2,
    "special_requests": "We would like an early check-in if possible."
  }'
```

## 🔧 Configuration

### Database Settings

The application supports multiple databases. PostgreSQL is recommended for production.

```python
# For PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wanderlust',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🗄️ Database Models

### Key Relationships

- **User** ↔ **Listing** (One-to-Many: Host owns listings)
- **User** ↔ **Booking** (One-to-Many: Guest makes bookings)
- **Listing** ↔ **Booking** (One-to-Many: Listing has bookings)
- **Booking** ↔ **Review** (One-to-One: Booking has one review)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support, please:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
