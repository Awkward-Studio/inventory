from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OrderCard, OrderPart
from inventory.models import Product
from .serializers import (
    OrderCardDetailSerializer,
    OrderPartSerializer,
    OrderCardCreateSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from django.db import IntegrityError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404


class OrderCardListView(APIView):
    """
    Get a list of all orders.
    """

    def get(self, request):
        orders = OrderCard.objects.all().order_by("-created_at")
        serializer = OrderCardDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCardCreateView(APIView):
    """
    Create a new order.
    """

    def post(self, request):
        serializer = OrderCardCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Attempt to save the order
                order = serializer.save()
                return Response(
                    OrderCardDetailSerializer(order).data,
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    {"error": "An integrity error occurred. Please try again."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderCardDetailView(APIView):
    """
    Retrieve details of a specific order.
    """

    def get(self, request, order_id):
        try:
            order = OrderCard.objects.get(id=order_id)
        except OrderCard.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderCardDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCardUpdateView(APIView):
    """
    Update order details.
    """

    def put(self, request, order_id):
        try:
            order = OrderCard.objects.get(id=order_id)
        except OrderCard.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderCardDetailSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderCardDetailSerializer(order).data,
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderCardDeleteView(APIView):
    """
    Delete an order.
    """

    def delete(self, request, order_id):
        try:
            order = OrderCard.objects.get(id=order_id)
            order.delete()
            return Response(
                {"message": "Order deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except OrderCard.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AddPartsToOrderView(APIView):
    """
    Handle adding, updating, or deleting multiple parts in an order.
    """

    def post(self, request, order_id):
        try:
            order = OrderCard.objects.get(id=order_id)
        except OrderCard.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        parts = request.data.get("parts", [])  # List of parts

        added_or_updated_parts = []  # To store added/updated parts
        deleted_parts = []  # To store deleted parts

        # Delete removed parts from db
        parts_in_db = OrderPart.objects.filter(order=order)
        received_part_ids = {part["part_id"] for part in parts}
        parts_to_delete = parts_in_db.exclude(part_id__in=received_part_ids)
        if parts_to_delete.exists():
            try:
                parts_to_delete.delete()
            except OrderPart.DoesNotExist:
                deleted_parts.append(
                    {"part_id": product_id, "message": "Part not found"}
                )

        for part_data in parts:
            product_id = part_data.get("part_id")
            quantity = int(part_data.get("quantity", 1))
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": f"Product with ID {product_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Create or update the OrderPart
            order_part, created = OrderPart.objects.get_or_create(
                order=order,
                product=product,
                part_id=product_id,
                defaults={
                    "quantity": quantity,
                },
            )

            code = status.HTTP_201_CREATED

            if not created:
                # If the part already exists, update the quantity and totals
                order_part.quantity = quantity
                order_part.save()
                code = status.HTTP_204_NO_CONTENT

            # Add the part to the response list
            added_or_updated_parts.append(OrderPartSerializer(order_part).data)

        return Response(
            {
                "added_or_updated_parts": added_or_updated_parts,
                "deleted_parts": deleted_parts,
            },
            status=code,
        )


class FinalizeOrderView(APIView):
    def post(self, request, order_id):
        try:
            order = OrderCard.objects.get(id=order_id)
        except OrderCard.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Deduct quantities from inventory
        for part in order.order_parts.all():
            try:
                product = Product.objects.get(id=part.part_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": f"Product with ID {part.part_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if product.quantity >= part.quantity:
                product.quantity -= part.quantity
                product.save()
            else:
                return Response(
                    {"error": f"Not enough stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Mark order as finalized
        order.status = "Finalized"
        order.save()

        return Response(
            {"message": "Order finalized and inventory updated."},
            status=status.HTTP_200_OK,
        )


class SendOTPView(APIView):
    """
    Generates and sends an OTP to the customer's email.
    """

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            order = get_object_or_404(
                OrderCard, id=serializer.validated_data["order_id"]
            )

            # Clear old OTP and generate a new one
            order.generate_otp_secret()
            otp_code = order.generate_otp()

            # Send OTP via email
            send_mail(
                subject="Order Verification OTP",
                message=f"Your OTP for order #{order.order_number} is {otp_code}. It is valid for 10 minutes.",
                from_email="atiqaxis7@gmail.com",
                recipient_list=[order.customer_email],
            )

            return Response(
                {"message": "OTP sent to customer's email."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    Verifies the OTP entered by the customer and marks the order as completed.
    """

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        isVerified = True
        if serializer.is_valid():
            order = get_object_or_404(
                OrderCard, id=serializer.validated_data["order_id"]
            )

            # Check if OTP has expired
            if order.is_otp_expired():
                isVerified = False
                return Response(
                    {
                        "isVerified": isVerified,
                        "error": "OTP has expired. Please request a new OTP.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify OTP
            if not order.verify_otp(serializer.validated_data["otp"]):
                isVerified = False
                return Response(
                    {"isVerified": isVerified, "error": "Invalid OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mark order as completed
            order.mark_as_completed()

            return Response(
                {
                    "isVerified": isVerified,
                    "message": "Order verified and marked as completed.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
