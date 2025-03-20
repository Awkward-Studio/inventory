from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import csv
import io
from datetime import datetime

from .models import Product, ProductMedia
from .serializers import (
    ProductListSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductUpdateSerializer,
    ProductMediaSerializer,
)

from .filters import ProductFilter


class ProductListView(APIView):
    """
    Handle GET requests to list all products with:
    - Filtering (price range, category, name, creation date)
    - Searching (name or other fields)
    - Ordering (ascending/descending)
    """

    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()

        # Apply filters using django-filter
        filterset = ProductFilter(data=request.GET, queryset=products)
        if filterset.is_valid():
            products = filterset.qs
        else:
            return Response(filterset.errors, status=400)

        # Apply ordering
        ordering = request.GET.get("ordering")
        if ordering:
            products = products.order_by(ordering)

        # Serialize and return the response
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=200)


class ProductCreateView(APIView):
    """
    Handle POST requests to create a new product.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        if isinstance(
            request.data, list
        ):  # Check if the request is for multiple entries
            serializer = ProductCreateSerializer(data=request.data, many=True)
        else:  # Single product creation
            serializer = ProductCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    """
    Handle GET requests to retrieve a specific product.
    """

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ProductUpdateView(APIView):
    """
    Handle PUT requests to update a product.
    """

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteView(APIView):
    """
    Handle DELETE requests to delete a product.
    """

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(
                {"message": "Product deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ProductMediaListView(APIView):
    """
    Fetch all media for all products
    """

    def get(self, request):
        try:
            media = ProductMedia.objects.all().order_by("-created_at")
            serializer = ProductMediaSerializer(media, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductMediaByProductView(APIView):
    """
    Fetch all media associated with a specific product
    """

    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            media = ProductMedia.objects.filter(product=product)
            serializer = ProductMediaSerializer(media, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateProductMediaView(APIView):
    """
    Create a new media entry for a product
    """

    def post(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            data = request.data.copy()
            data["product"] = product.id  # Ensure product ID is assigned correctly

            serializer = ProductMediaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateProductMediaView(APIView):
    """
    Update an existing product media entry.
    """

    def patch(self, request, media_id):
        """
        Partial update for media (e.g., update only `appwrite_file_id` or `media_type`).
        """
        try:
            media = get_object_or_404(ProductMedia, id=media_id)
            serializer = ProductMediaSerializer(
                media, data=request.data, partial=True
            )  # Partial update

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteProductMediaView(APIView):
    """
    Delete a media entry by ID
    """

    def delete(self, request, media_id):
        try:
            media = get_object_or_404(ProductMedia, id=media_id)
            deleted_media_appwrite_id = str(
                media.appwrite_file_id
            )  # Store ID before deletion
            media.delete()
            return Response(
                {
                    "message": "Media deleted successfully",
                    "appwrite_file_id": deleted_media_appwrite_id,
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetProductMediaByIdView(APIView):
    """
    Fetch a single product media entry by its ID
    """

    def get(self, request, media_id):
        try:
            media = get_object_or_404(ProductMedia, id=media_id)
            serializer = ProductMediaSerializer(media)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductCsvUploadView(APIView):
    """
    Handle CSV uploads to create products in the database.
    """

    def post(self, request):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"error": "No CSV file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            return Response(
                {"error": f"Failed to read CSV file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_products = []
        errors = []
        row_number = 1

        for row in reader:
            try:
                product = Product(
                    name=row.get("name"),
                    itemCode=row.get("itemCode") or None,
                    sku=row.get("sku") or None,
                    hsn=row.get("hsn") or None,
                    category=row.get("category") or None,
                    quantity=int(row.get("quantity", 0)),
                    itemLocation=row.get("itemLocation") or None,
                    description=row.get("description") or None,
                    price=row.get("price"),
                    msp=row.get("msp") or None,
                    mrp=row.get("mrp") or None,
                    gst=row.get("gst") or None,
                    cgst=row.get("cgst") or None,
                    sgst=row.get("sgst") or None,
                    igst=row.get("igst") or None,
                    vendorCode=row.get("vendorCode") or None,
                    vendorName=row.get("vendorName") or None,
                    purchasePrice=row.get("purchasePrice") or None,
                    purchaseLocation=row.get("purchaseLocation") or None,
                    purchaseOrderId=row.get("purchaseOrderId") or None,
                    warrantyPeriod=row.get("warrantyPeriod") or None,
                    mobis_status=row.get("mobis_status", Product.NON_MOBIS),
                )

                # Parse dates if provided (expected format: YYYY-MM-DD)
                if row.get("purchaseOrderDate"):
                    product.purchaseOrderDate = datetime.strptime(
                        row["purchaseOrderDate"], "%Y-%m-%d"
                    ).date()
                if row.get("lastUpdatedDate"):
                    product.lastUpdatedDate = datetime.strptime(
                        row["lastUpdatedDate"], "%Y-%m-%d"
                    ).date()

                product.save()
                created_products.append(str(product.id))
            except Exception as e:
                errors.append(f"Row {row_number}: {str(e)}")
            row_number += 1

        return Response(
            {"created_products": created_products, "errors": errors},
            status=status.HTTP_200_OK,
        )
