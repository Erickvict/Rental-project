from django.contrib import admin
from .models import Vehicle, VehicleDocument, Cart, CartItem,BookingDetails,Order, OrderItem


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'brand',
        'model',
        'transmission',
        'fuel_type',
        'hourly_price',
        'daily_price',
        'own_rent_price',
        'status',
        'created_at',
    )


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle",
        "created_at",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created_at",
        "updated_at",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "vehicle",
        "quantity",
    )



@admin.register(BookingDetails)
class BookingDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "full_name",
        "email",
        "phone_number",
        "rental_start",
        "rental_end",
        "location",
        "created_at",
    )



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order_number",
        "user",
        "total_amount",
        "order_status",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "order_status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "vehicle",
        "vehicle_name",
        "plan",
        "hours",
        "quantity",
        "price",
        "subtotal",
    )

    list_filter = (
        "plan",
    )

    search_fields = (
        "vehicle_name",
        "order__order_number",
    )