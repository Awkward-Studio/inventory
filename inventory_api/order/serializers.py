from rest_framework import serializers
from .models import OrderCard, OrderPart
from inventory.serializers import ProductListSerializer


class OrderPartSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderPart
        fields = [
            "id",
            "order",
            "part_id",
            "quantity",
            "product",
            "created_at",
        ]


class OrderCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCard
        fields = [
            "id",
            "customer_name",
            "customer_address",
            "customer_phone",
            "customer_email",
            "customer_gst",
            "customer_chassis_or_engine_num",
            "status",
            "discount_amount",
            "sub_total",
            "cgst_amount",
            "sgst_amount",
            "team_lead",
            "sales_executive",
            "total_tax",
            "total_amount",
        ]


class OrderCardDetailSerializer(serializers.ModelSerializer):
    order_parts = OrderPartSerializer(many=True)

    class Meta:
        model = OrderCard
        fields = [
            "id",
            "order_number",
            "customer_name",
            "customer_address",
            "customer_email",
            "customer_phone",
            "customer_gst",
            "status",
            "order_parts",
            "progress_status",
            "customer_chassis_or_engine_num",
            "otp_generated_at",
            "created_at",
            "discount_amount",
            "sub_total",
            "cgst_amount",
            "sgst_amount",
            "team_lead",
            "sales_executive",
            "total_tax",
            "total_amount",
        ]


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP to customer email."""

    order_id = serializers.UUIDField()


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and completing order."""

    order_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6)
