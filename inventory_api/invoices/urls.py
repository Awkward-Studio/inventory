from django.urls import path
from .views import (
    GetNextInvoiceNumberView,
    CreateInvoiceView,
    InvoiceListView,
    InvoiceDetailView,
)

urlpatterns = [
    path(
        "invoices/next/<uuid:order_id>/<str:invoice_type>/",
        GetNextInvoiceNumberView.as_view(),
        name="get-next-invoice-number",
    ),
    path("invoices/<uuid:order_id>/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/create/", CreateInvoiceView.as_view(), name="create-invoice"),
    path(
        "invoices/<uuid:invoice_id>/",
        InvoiceDetailView.as_view(),
        name="invoice-detail",
    ),
    path(
        "invoices/<uuid:invoice_id>/update/",
        InvoiceDetailView.as_view(),
        name="invoice-update",
    ),
]
