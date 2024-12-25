from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Product
from .serializers import (
    ProductListSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductUpdateSerializer,
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

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductUpdateSerializer(product, data=request.data)
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
