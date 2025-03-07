from rest_framework import serializers
from .models import Product, ProductMedia


class ProductMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductMedia model
    """

    class Meta:
        model = ProductMedia
        fields = ["id", "product", "media_type", "appwrite_file_id", "created_at"]
        read_only_fields = ["id", "created_at"]  # Prevent modification of these fields


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
            "vendorCode",
            "purchasePrice",
            "purchaseLocation",
            "purchaseOrderDate",
            "purchaseOrderId",
            "warrantyPeriod",
            "mobis_status",
            "created_at",
            "updated_at",
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
            "mobis_status",
            "created_at",
            "updated_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a product's details with media included.
    """

    media = ProductMediaSerializer(many=True, read_only=True)

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
            "mobis_status",
            "created_at",
            "updated_at",
        ]
