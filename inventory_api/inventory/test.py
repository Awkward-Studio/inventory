from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product


class ProductAPITestCase(APITestCase):
    def setUp(self):
        # Create some sample products
        Product.objects.create(
            name="Wireless Headphones",
            sku="WH-2024",
            category="Electronics",
            price=199.99,
            quantity=50,
        )
        Product.objects.create(
            name="Gaming Laptop",
            sku="GL-456",
            category="Computers",
            price=1299.99,
            quantity=20,
        )

    def test_list_products(self):
        """Test listing all products"""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_category(self):
        """Test filtering products by category"""
        response = self.client.get("/products/?category=Electronics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Wireless Headphones")

    def test_filter_by_price_range(self):
        """Test filtering products by price range"""
        response = self.client.get("/products/?min_price=100&max_price=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Wireless Headphones")

    def test_ordering(self):
        """Test ordering products by price descending"""
        response = self.client.get("/products/?ordering=-price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["name"], "Gaming Laptop"
        )  # Most expensive product

    def test_create_product(self):
        """Test creating a new product"""
        data = {
            "name": "Smartphone",
            "sku": "SP-789",
            "category": "Electronics",
            "price": 799.99,
            "quantity": 100,
        }
        response = self.client.post("/products/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Smartphone")
