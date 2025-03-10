from django.urls import path
from .views import (
    OrderCardListView,
    OrderCardCreateView,
    OrderCardDetailView,
    OrderCardUpdateView,
    OrderCardDeleteView,
    AddPartsToOrderView,
    FinalizeOrderView,
    SendOTPView,
    VerifyOTPView,
)

urlpatterns = [
    path("orders/", OrderCardListView.as_view(), name="order-list"),
    path("orders/create/", OrderCardCreateView.as_view(), name="order-create"),
    path("orders/<uuid:order_id>/", OrderCardDetailView.as_view(), name="order-detail"),
    path(
        "orders/<uuid:order_id>/update/",
        OrderCardUpdateView.as_view(),
        name="order-update",
    ),
    path(
        "orders/<uuid:order_id>/delete/",
        OrderCardDeleteView.as_view(),
        name="order-delete",
    ),
    path(
        "orders/<uuid:order_id>/add-parts/",
        AddPartsToOrderView.as_view(),
        name="add-parts",
    ),
    path(
        "orders/<uuid:order_id>/finalize/",
        FinalizeOrderView.as_view(),
        name="finalize-order",
    ),
    path("orders/send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("orders/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]
