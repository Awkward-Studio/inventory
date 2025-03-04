from django.db import models, transaction
import uuid
from order.models import OrderCard


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_card = models.ForeignKey(
        OrderCard, related_name="invoices", on_delete=models.CASCADE
    )
    invoice_type = models.CharField(max_length=50)  # e.g., "Quote", "Tax Invoice"
    invoice_number = models.PositiveIntegerField()  # Global consecutive number
    invoice_url = models.URLField()  # Store ImageKit URL instead of a file
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "order_card",
            "invoice_type",
            "invoice_number",
        )  # Ensures invoices of same type for an order share the same number
        ordering = ["invoice_number"]  # Sort invoices by number

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.invoice_type} for Order {self.order_card.order_number}"

    @classmethod
    def get_next_invoice_number(cls) -> int:
        """
        Fetch the next available invoice number globally across all orders.
        Uses transaction locking to prevent concurrency issues.
        """
        with transaction.atomic():  # Prevents race conditions
            last_invoice = (
                cls.objects.select_for_update().order_by("-invoice_number").first()
            )
            next_invoice_number = last_invoice.invoice_number + 1 if last_invoice else 1
            return next_invoice_number

    @classmethod
    def get_or_create_invoice_number(
        cls, order_card: OrderCard, invoice_type: str
    ) -> int:
        """
        Get the invoice number for a specific order and invoice type.
        Ensures that invoices of the same type in the same `OrderCard` share the same number.
        """
        with transaction.atomic():
            # Check if this `invoice_type` already has a number assigned for the given order
            existing_invoice = cls.objects.filter(
                order_card=order_card, invoice_type=invoice_type
            ).first()

            if existing_invoice:
                return (
                    existing_invoice.invoice_number
                )  # ✅ Return the existing invoice number

            # Otherwise, get the next global invoice number
            return cls.get_next_invoice_number()
