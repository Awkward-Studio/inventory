from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "order_card",
            "invoice_type",
            "invoice_number",
            "invoice_url",
            "created_at",
        ]
        read_only_fields = [
            "invoice_number",
            "order_card",
            "invoice_type",
        ]  # Prevents modifying these fields on update


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Used for updating an invoice, allowing only `invoice_url` to be modified.
    """

    class Meta:
        model = Invoice
        fields = ["invoice_url"]
