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
            "category",
            "quantity",
            "price",
            "description",
            "supplier",
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
            "category",
            "quantity",
            "price",
            "description",
            "supplier",
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
            "category",
            "quantity",
            "price",
            "description",
            "supplier",
        ]
