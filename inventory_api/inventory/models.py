from django.db import models
import uuid


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    itemCode = models.DecimalField(
        max_digits=100, decimal_places=0, null=True, blank=True
    )
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    itemLocation = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    msp = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    sgst = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    igst = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    vendorCode = models.CharField(max_length=50, blank=True, null=True)
    vendorName = models.CharField(max_length=100, blank=True, null=True)
    purchasePrice = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    purchaseLocation = models.CharField(max_length=500, blank=True, null=True)
    purchaseDate = models.DateField(null=True, blank=True)
    purchaseOrderDate = models.DateField(null=True, blank=True)
    purchaseOrderId = models.CharField(max_length=50, blank=True, null=True)
    lastUpdatedDate = models.DateField(null=True, blank=True)
    warrantyPeriod = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
