from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

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
