from rest_framework import serializers
from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing products.
    """

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "hsn",
            "category",
            "quantity",
            "price",
            "description",
            "itemCode",
            "itemLocation",
            "msp",
            "mrp",
            "gst",
            "cgst",
            "sgst",
            "igst",
            "vendorName",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new product.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "hsn",
            "category",
            "quantity",
            "price",
            "description",
            "itemCode",
            "itemLocation",
            "msp",
            "mrp",
            "gst",
            "cgst",
            "sgst",
            "igst",
            "vendorCode",
            "vendorName",
            "purchasePrice",
            "purchaseLocation",
            "purchaseOrderDate",
            "purchaseOrderId",
            "warrantyPeriod",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a product's details.
    """

    class Meta:
        model = Product
        fields = "__all__"


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a product.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "hsn",
            "category",
            "quantity",
            "price",
            "description",
            "itemCode",
            "itemLocation",
            "msp",
            "mrp",
            "gst",
            "cgst",
            "sgst",
            "igst",
            "vendorCode",
            "vendorName",
            "purchasePrice",
            "purchaseLocation",
            "purchaseOrderDate",
            "purchaseOrderId",
            "warrantyPeriod",
        ]
