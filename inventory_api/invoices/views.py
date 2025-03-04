from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from order.models import OrderCard
from .models import Invoice
from .serializers import InvoiceSerializer
from django.db import transaction


class GetNextInvoiceNumberView(APIView):
    """
    Fetch the next available invoice number globally (across all orders).
    If an invoice of the same type already exists for an order, return its number.
    """

    def get(self, request, order_id, invoice_type):
        try:
            order_card = get_object_or_404(OrderCard, id=order_id)
            invoice_number = Invoice.get_or_create_invoice_number(
                order_card, invoice_type
            )
            return Response(
                {"invoice_number": invoice_number}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateInvoiceView(APIView):
    """
    Create an invoice **only after generating the invoice document**.
    Ensures that the invoice number follows the correct sequence.
    """

    def post(self, request):
        try:
            order_card_id = request.data.get("order_card")
            invoice_type = request.data.get("invoice_type")
            invoice_url = request.data.get("invoice_url")

            if not order_card_id or not invoice_type or not invoice_url:
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order_card = get_object_or_404(OrderCard, id=order_card_id)

            # Ensure correct invoice number assignment
            invoice_number = Invoice.get_or_create_invoice_number(
                order_card, invoice_type
            )

            # Save the invoice record
            with transaction.atomic():
                invoice = Invoice.objects.create(
                    order_card=order_card,
                    invoice_type=invoice_type,
                    invoice_number=invoice_number,
                    invoice_url=invoice_url,
                )

            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvoiceListView(APIView):
    """
    Fetch all invoices.
    """

    def get(self, request, order_id):
        try:
            order_card = get_object_or_404(OrderCard, id=order_id)
            invoices = Invoice.objects.filter(order_card=order_card).order_by(
                "invoice_number"
            )
            serializer = InvoiceSerializer(invoices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvoiceDetailView(APIView):
    """
    Fetch, update, or delete a single invoice.
    """

    def get(self, request, invoice_id):
        """
        Retrieve a single invoice by ID.
        """
        try:
            invoice = get_object_or_404(Invoice, id=invoice_id)
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, invoice_id):
        """
        Update an existing invoice.
        Only `invoice_url` can be updated.
        """
        try:
            invoice = get_object_or_404(Invoice, id=invoice_id)
            invoice_url = request.data.get("invoice_url")

            if not invoice_url:
                return Response(
                    {"error": "Invoice URL is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            invoice.invoice_url = invoice_url
            invoice.save()

            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, invoice_id):
        """
        Delete an invoice.
        """
        try:
            invoice = get_object_or_404(Invoice, id=invoice_id)
            invoice.delete()
            return Response(
                {"message": "Invoice deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
