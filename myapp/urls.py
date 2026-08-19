from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.home),
    path("services/", views.services),
    path("contact/", views.contact),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="pages/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("user/", views.vehicle_list, name="vehicle_list"),
    path("vehicle/<int:vehicle_id>/", views.vehicle_detail, name="vehicle_detail"),
    path("cart/add/<int:vehicle_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/update/<int:item_id>/",
        views.update_cart_quantity,
        name="update_cart_quantity",
    ),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart, name="cart"),
    path("booking-details/", views.booking_details, name="booking_details"),
    path("order-review/<int:order_id>/", views.order_review, name="order_review"),
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path(
        "payment-success/<int:order_id>/", views.payment_success, name="payment_success"
    ),
    path("checkout/", views.checkout, name="checkout"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
