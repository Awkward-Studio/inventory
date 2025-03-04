from django.db import models, transaction
import uuid


class OrderCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.PositiveIntegerField(unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    customer_phone = models.CharField(max_length=15)
    customer_gst = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=50, default="Pending"
    )  # "Pending", "Finalized"
    progress_status = models.PositiveIntegerField(
        default=1
    )  # 1 = Save, 2 = Quote, 3 = Tax Invoice
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If this is a new order, assign the next available order number
        if not self.order_number:
            with transaction.atomic():  # Ensure atomicity
                # Lock the table to prevent race conditions
                last_order = (
                    OrderCard.objects.select_for_update()
                    .order_by("-order_number")
                    .first()
                )
                if last_order:
                    self.order_number = last_order.order_number + 1
                else:
                    self.order_number = 1  # Start at 1 if no orders exist

        super().save(*args, **kwargs)  # Call the base save method

    def __str__(self):
        return f"Order by {self.customer_name} - {self.id} - {self.order_number}"


class OrderPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        OrderCard, related_name="order_parts", on_delete=models.CASCADE
    )

    # Storing a snapshot of the product details at the time of the order
    part_id = models.CharField(
        max_length=100
    )  # Product ID (if needed for quantity updates)
    part_name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=50)
    hsn = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # Pricing and tax details
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Editable per order
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # Editable per order
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # Calculated field
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated field
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated field
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Calculated field

    # Fixed GST values from the original product
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    cgst_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    sgst_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        """
        Calculate subtotal, tax, and total amount for this OrderPart.
        """

        from decimal import Decimal

        # Ensure all numerical values are of type Decimal
        mrp_sub_total = Decimal(self.mrp) * Decimal(self.quantity)
        discount_amount = Decimal(mrp_sub_total) * (
            Decimal(self.discount) / Decimal(100)
        )
        sub_total = Decimal(mrp_sub_total) - Decimal(discount_amount)
        cgst_amount = Decimal(sub_total) * (Decimal(self.cgst) / Decimal(100))
        sgst_amount = Decimal(sub_total) * (Decimal(self.sgst) / Decimal(100))
        total_tax_amount = Decimal(cgst_amount) + Decimal(sgst_amount)
        total_amount = Decimal(sub_total) + Decimal(total_tax_amount)

        self.discount_amount = discount_amount
        self.sub_total = sub_total
        self.cgst_amount = cgst_amount
        self.sgst_amount = sgst_amount
        self.total_tax = total_tax_amount
        self.total_amount = total_amount
