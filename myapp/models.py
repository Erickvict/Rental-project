from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    STATUS = [
        ('Available','Available'),
        ('Booked','Booked'),
        ('Maintenance','Under Maintenance'),
        ('Reserved','Reserved'),
        ('Out','Out of Service'),
    ]
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]

    TRANSMISSION_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]

    brand = models.CharField(max_length=100)


    image = models.ImageField(
        upload_to='vehicles/',
        blank=True,
        null=True
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)

    seating_capacity = models.IntegerField()
    luggage_capacity = models.IntegerField()

    hourly_price=models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100
    )
    daily_price=models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=700
    )
    own_rent_price=models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=10000
    )
    
    rating = models.FloatField(default=0)

    bookings = models.IntegerField(default=0)

    status=models.CharField(
        max_length=20,
        choices=STATUS,
        default="Available"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand}"






class VehicleDocument(models.Model):

    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    rc_document = models.FileField(
        upload_to="vehicle_documents/rc/"
    )

    insurance_document = models.FileField(
        upload_to="vehicle_documents/insurance/"
    )

    pollution_document = models.FileField(
        upload_to="vehicle_documents/pollution/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Documents - {self.vehicle}"






class Cart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Cart - {self.user.username}"



    @property
    def total_items(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def total_price(self):
        return sum(
            item.price * item.quantity
            for item in self.items.all()
        )


class CartItem(models.Model):

    PLAN_CHOICES = [
        ("hourly", "Hourly"),
        ("daily", "24 Hours"),
        ("own", "Own Rent"),
    ]

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES
    )
    hours = models.PositiveIntegerField(
        default=1
    )
    quantity = models.PositiveIntegerField(
        default=1
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.vehicle} - {self.plan}"



class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    PAYMENT_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=20,
        unique=True
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT
    )

    vehicle_name = models.CharField(
        max_length=200
    )

    plan = models.CharField(
        max_length=20
    )

    hours = models.PositiveIntegerField(
        default=1
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.vehicle_name}"






class BookingDetails(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="booking_details"
    )

    full_name = models.CharField(
        max_length=200
    )

    dob = models.DateField()

    email = models.EmailField()

    phone_number = models.CharField(
        max_length=15
    )

    guardian_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    guardian_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    aadhar_number = models.CharField(
        max_length=12
    )

    driving_license_number = models.CharField(
        max_length=50
    )

    rental_start = models.DateTimeField()

    rental_end = models.DateTimeField()

    address = models.TextField()

    location = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.order.order_number}"