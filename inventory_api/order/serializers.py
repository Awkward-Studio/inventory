from rest_framework import serializers
from .models import OrderCard, OrderPart


class OrderPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPart
        fields = [
            "id",
            "order",
            "part_id",
            "part_name",
            "part_number",
            "hsn",
            "quantity",
            "mrp",
            "discount",
            "discount_amount",
            "sub_total",
            "gst",
            "cgst",
            "sgst",
            "cgst_amount",
            "sgst_amount",
            "total_tax",
            "total_amount",
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
        ]


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP to customer email."""

    order_id = serializers.UUIDField()


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and completing order."""

    order_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6)
