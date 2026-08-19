from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.auth import login as auth_login
from .models import Vehicle, Cart, CartItem
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
from django.contrib import messages
from datetime import date, timedelta
from django.utils.dateparse import parse_datetime
import uuid
from django.conf import settings
import calendar
from datetime import date, timedelta
from .utils import generate_booking_pdf
from .models import (
    Cart,
    Order,
    OrderItem,
    BookingDetails,
)


def home(request):

    if request.user.is_authenticated:
        return render(request, "pages/dashboard.html")

    return render(request, "pages/index.html")


def services(request):
    return render(request, "pages/services.html")


def contact(request):
    return render(request, "pages/contact.html")


def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data["password1"])

            user.save()
            auth_login(request, user)

            return redirect("login")

    else:
        form = SignupForm()

    return render(request, "pages/signup.html", {"form": form})


@login_required
def vehicle_list(request):

    vehicles = Vehicle.objects.all()

    brand = request.GET.get("brand")
    fuel = request.GET.get("fuel")
    transmission = request.GET.get("transmission")

    is_filtered = False
    if fuel:
        vehicles = vehicles.filter(fuel_type=fuel)
        is_filtered = True

    if transmission:
        vehicles = vehicles.filter(transmission=transmission)
        is_filtered = True

    if brand:
        vehicles = vehicles.filter(brand=brand)
        is_filtered = True

    sort = request.GET.get("sort")

    if sort == "newest":

        vehicles = vehicles.order_by("-created_at")
        is_filtered = True

    elif sort == "popular":

        vehicles = vehicles.order_by("-bookings")
        is_filtered = True

    elif sort == "reviews":

        vehicles = vehicles.order_by("-rating")
        is_filtered = True

    return render(
        request,
        "pages/dashboard.html",
        {
            "vehicles": vehicles,
            "is_filtered": is_filtered,
            "user": request.user,
        },
    )


def vehicle_detail(request, vehicle_id):

    vehicle = get_object_or_404(
        Vehicle.objects.select_related("documents"), id=vehicle_id
    )

    today = timezone.localdate()

    year = today.year
    month = today.month

    first_day = date(year, month, 1)

    last_day = date(year, month, calendar.monthrange(year, month)[1])

    bookings = BookingDetails.objects.filter(
        order__items__vehicle=vehicle,
        order__order_status__in=["pending", "confirmed"],
        rental_start__date__lte=last_day,
        rental_end__date__gte=first_day,
    )

    first_weekday = first_day.weekday()

    starting_blanks = (first_weekday + 1) % 7

    calendar_days = []

    for _ in range(starting_blanks):
        calendar_days.append({"date": None, "bookings": []})

    current_day = first_day

    while current_day <= last_day:

        day_bookings = []

        for booking in bookings:

            start_date = booking.rental_start.date()
            end_date = booking.rental_end.date()

            if start_date <= current_day <= end_date:
                day_bookings.append(booking)

        calendar_days.append({"date": current_day, "bookings": day_bookings})

        current_day += timedelta(days=1)

    return render(
        request,
        "pages/vehicle_detail.html",
        {
            "vehicle": vehicle,
            "month": first_day,
            "calendar_days": calendar_days,
            "bookings": bookings,
            "today": today,
        },
    )


@login_required
@require_POST
def add_to_cart(request, vehicle_id):

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    plan = request.POST.get("plan")
    hours = request.POST.get("hours")

    if plan == "hourly":
        hours = int(hours or 1)
        price = vehicle.hourly_price * hours

    elif plan == "daily":
        price = vehicle.daily_price

    elif plan == "own":
        price = vehicle.own_rent_price

    else:
        return JsonResponse(
            {"success": False, "message": "Please select a rental plan."}, status=400
        )

    cart, cart_created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        vehicle=vehicle,
        plan=plan,
        defaults={"quantity": 1, "price": price, "hours": hours},
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":

        return JsonResponse(
            {
                "success": True,
                "cart_count": cart.total_items,
                "message": f"{vehicle.brand} added to cart! 🛒",
            }
        )

    return redirect("cart")


@login_required
def cart(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return render(request, "pages/cart.html", {"cart_items": []})

    cart_items = cart.items.select_related("vehicle")

    return render(
        request,
        "pages/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
        },
    )

@login_required
def checkout(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        return redirect("cart")

    order = Order.objects.filter(
        user=request.user,
        order_status="pending",
        payment_status="pending",
    ).order_by("-id").first()

    if order:
        return redirect("order_review", order_id=order.id)

    return redirect("booking_details")




@login_required
@require_POST
def update_cart_quantity(request, item_id):

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    action = request.POST.get("action")

    if action == "increase":
        item.quantity += 1
        item.save()

    elif action == "decrease":

        if item.quantity > 1:
            item.quantity -= 1
            item.save()

        else:
            item.delete()

    else:
        return JsonResponse(
            {"success": False, "message": "Invalid action."}, status=400
        )

    cart = item.cart if item.pk else Cart.objects.get(user=request.user)

    return JsonResponse(
        {
            "success": True,
            "quantity": item.quantity if item.pk else 0,
            "subtotal": (item.price * item.quantity if item.pk else 0),
            "cart_count": cart.total_items,
            "cart_total": cart.total_price,
            "removed": not item.pk,
        }
    )


@login_required
@require_POST
def remove_from_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    item.delete()

    cart = Cart.objects.get(user=request.user)

    return JsonResponse(
        {
            "success": True,
            "cart_count": cart.total_items,
            "cart_total": cart.total_price,
            "message": "Item removed from cart.",
        }
    )


@login_required
def booking_details(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        return redirect("cart")

    cart_items = cart.items.select_related("vehicle")

    if request.method == "POST":

        full_name = request.POST.get("f_name")
        dob = request.POST.get("d_ob")
        email = request.POST.get("email_id")
        phone_number = request.POST.get("phone_number")

        guardian_name = request.POST.get("g_name")
        guardian_phone = request.POST.get("g_phone")

        aadhar_number = request.POST.get("aadhar_no")
        driving_license_number = request.POST.get("driving_no")

        rental_start = request.POST.get("rental_start")
        rental_end = request.POST.get("rental_end")

        address = request.POST.get("add_ress")
        location = request.POST.get("loc_ation")

        rental_start = parse_datetime(rental_start)
        rental_end = parse_datetime(rental_end)

        if not rental_start or not rental_end:
            messages.error(request, "Please enter valid rental start and end dates.")
            return render(
                request,
                "pages/booking_details.html",
                {
                    "cart": cart,
                    "cart_items": cart_items,
                    "form_data": request.POST,
                },
            )

        if rental_start >= rental_end:
            messages.error(request, "Rental end date must be after rental start date.")
            return render(
                request,
                "pages/booking_details.html",
                {
                    "cart": cart,
                    "cart_items": cart_items,
                    "form_data": request.POST,
                },
            )

        for item in cart_items:

            overlapping_booking = BookingDetails.objects.filter(
                order__items__vehicle=item.vehicle,
                order__order_status__in=["pending", "confirmed"],
                rental_start__lt=rental_end,
                rental_end__gt=rental_start,
            ).exists()

            if overlapping_booking:
                messages.error(
                    request,
                    f"{item.vehicle.brand} is already booked "
                    f"for the selected dates.",
                )
                return render(
                    request,
                    "pages/booking_details.html",
                    {
                        "cart": cart,
                        "cart_items": cart_items,
                        "form_data": request.POST,
                    },
                )

        total_amount = sum(item.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
            total_amount=total_amount,
            order_status="pending",
            payment_status="pending",
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                vehicle=item.vehicle,
                vehicle_name=item.vehicle.brand,
                plan=item.plan,
                hours=item.hours,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.price * item.quantity,
            )

        BookingDetails.objects.create(
            order=order,
            full_name=full_name,
            dob=dob,
            email=email,
            phone_number=phone_number,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            aadhar_number=aadhar_number,
            driving_license_number=driving_license_number,
            rental_start=rental_start,
            rental_end=rental_end,
            address=address,
            location=location,
        )

        return redirect("order_review", order_id=order.id)

    return render(
        request,
        "pages/booking_details.html",
        {
            "cart": cart,
            "cart_items": cart_items,
        },
    )


@login_required
def order_review(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(
        request,
        "pages/order_review.html",
        {
            "order": order,
            "booking": order.booking_details,
        },
    )


@login_required
def payment(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, "pages/payment.html", {"order": order})


@login_required
def payment_success(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    order.payment_status = "paid"
    order.order_status = "confirmed"
    order.save()

    # Clear cart
    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        cart.items.all().delete()

    # Generate PDF
    pdf = generate_booking_pdf(order)

    # Save PDF temporarily for testing
    with open(f"booking_{order.order_number}.pdf", "wb") as file:
        file.write(pdf.getvalue())

    return render(request, "pages/payment_success.html", {"order": order})
