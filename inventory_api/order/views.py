from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OrderCard, OrderPart
from inventory.models import Product
from .serializers import (
    OrderCardDetailSerializer,
    OrderPartSerializer,
    OrderCardCreateSerializer,
)
from django.db import IntegrityError
from decimal import Decimal


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
            mrp = Decimal(part_data.get("mrp", 0))  # Editable per part
            discount = int(part_data.get("discount", 0))  # Editable per part

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": f"Product with ID {product_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch product details
            gst = product.gst
            cgst = product.cgst
            sgst = product.sgst
            part_name = product.name
            part_number = product.sku
            hsn = product.hsn

            # If quantity is 0, delete the part if it exists
            if quantity == 0:
                try:
                    order_part = OrderPart.objects.get(order=order, part_id=product_id)
                    order_part.delete()
                    deleted_parts.append(
                        {"part_id": product_id, "message": "Part deleted"}
                    )
                except OrderPart.DoesNotExist:
                    deleted_parts.append(
                        {"part_id": product_id, "message": "Part not found"}
                    )
                continue

            # Calculate totals
            # Ensure all numerical values are of type Decimal
            mrp_sub_total = Decimal(mrp) * Decimal(quantity)
            discount_amount = Decimal(mrp_sub_total) * (
                Decimal(discount) / Decimal(100)
            )
            sub_total = Decimal(mrp_sub_total) - Decimal(discount_amount)
            cgst_amount = Decimal(sub_total) * (Decimal(cgst) / Decimal(100))
            sgst_amount = Decimal(sub_total) * (Decimal(sgst) / Decimal(100))
            total_tax_amount = Decimal(cgst_amount) + Decimal(sgst_amount)
            total_amount = Decimal(sub_total) + Decimal(total_tax_amount)

            # Create or update the OrderPart
            order_part, created = OrderPart.objects.get_or_create(
                order=order,
                part_id=product_id,
                defaults={
                    "quantity": quantity,
                    "mrp": mrp,
                    "discount": discount,
                    "discount_amount": discount_amount,
                    "sub_total": sub_total,
                    "gst": gst,
                    "cgst": cgst,
                    "sgst": sgst,
                    "cgst_amount": cgst_amount,
                    "sgst_amount": sgst_amount,
                    "total_tax": total_tax_amount,
                    "total_amount": total_amount,
                    "part_name": part_name,
                    "part_number": part_number,
                    "hsn": hsn,
                },
            )

            code = status.HTTP_201_CREATED

            if not created:
                # If the part already exists, update the quantity and totals
                order_part.quantity = quantity  # Update to the new quantity
                order_part.mrp = mrp  # Update the MRP if it changed
                order_part.discount = discount  # Update discount if provided
                order_part.calculate_totals()
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
