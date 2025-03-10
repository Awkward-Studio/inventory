from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView,
    ProductMediaListView,
    ProductMediaByProductView,
    CreateProductMediaView,
    GetProductMediaByIdView,
    UpdateProductMediaView,
    DeleteProductMediaView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/create/", ProductCreateView.as_view(), name="product-create"),
    path("products/<uuid:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "products/<uuid:pk>/update/", ProductUpdateView.as_view(), name="product-update"
    ),
    path(
        "products/<uuid:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"
    ),
    path("products/media/", ProductMediaListView.as_view(), name="all-product-media"),
    path(
        "products/<uuid:product_id>/media/",
        ProductMediaByProductView.as_view(),
        name="product-media",
    ),
    path(
        "products/<uuid:product_id>/media/create/",
        CreateProductMediaView.as_view(),
        name="create-product-media",
    ),
    path(
        "products/media/<uuid:media_id>/update/",
        UpdateProductMediaView.as_view(),
        name="update-product-media",
    ),
    path(
        "products/media/<uuid:media_id>/delete/",
        DeleteProductMediaView.as_view(),
        name="delete-product-media",
    ),
    path(
        "products/media/<uuid:media_id>/",
        GetProductMediaByIdView.as_view(),
        name="get_product_media_by_id",
    ),
]
