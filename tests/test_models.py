# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

    def test_update_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        original_product_id = product.id
        description = 'New product description'
        product.description = description
        product.update()
        self.assertEqual(product.id, original_product_id)
        self.assertEqual(product.description, description)

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_product_id)
        self.assertEqual(products[0].description, description)

        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_deserialize_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()

        name = product.name
        description = product.description
        price = product.price
        available = product.available
        category = product.category
        data = product.serialize()
        self.assertIsNotNone(data)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

        product = Product()
        product.deserialize(data)
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(product.name, name)
        self.assertEqual(product.description, description)
        self.assertEqual(product.price, price)
        self.assertEqual(product.available, available)
        self.assertEqual(product.category, category)

        # product.available = 'available'
        # self.assertRaises(DataValidationError, product.update)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        # Use a for loop to iterate over the products list and call the create() method
        # on each product to save them to the database.
        for product in products:
            product.create()
        new_products = Product.all()
        self.assertEqual(len(new_products), 5)
        # Retrieve the name of the first product in the products list.
        name = products[0].name
        # Use a list comprehension to filter the products based on their name 
        # and then use len() to calculate the length of the filtered list, and use the variable called count
        # to hold the number of products that match the name.
        filtered_products = [product for product in Product.all() if product.name == name]
        self.assertEqual(len(filtered_products), 1)

        # Call the find_by_name() method on the Product class
        # to retrieve products from the database that have the specified name.
        found_products = Product.find_by_name(name)
        
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), 1)

        # Use a for loop to iterate over the found products and assert that each product's name matches the expected name, to ensure that all the retrieved products have the correct name.
        for idx, product in enumerate(found_products):
            self.assertEqual(product.name, products[idx].name)

    def test_find(self):
        """It should Find a Product by ID"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        found_product = Product.find(products[0].id)
        self.assertEqual(products[0].id, found_product.id)

    def test_find_by_price(self):
        """It should Find a Product by price"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        found_product = Product.find_by_price(products[0].price)
        self.assertEqual(products[0].id, found_product[0].id)

        found_product = Product.find_by_price(str(products[0].price))
        self.assertEqual(products[0].id, found_product[0].id)


    def test_find_by_availability(self):
        """It should Find a Product by availability"""
        available_products = []
        not_available_products = []
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
            if product.available == True:
                available_products.append(product)
            else:
                not_available_products.append(product)

        found_products = Product.find_by_availability(True)
        self.assertEqual(len(available_products), found_products.count())

        found_products = Product.find_by_availability(False)
        self.assertEqual(len(not_available_products), found_products.count())

    def test_find_by_category(self):
        """It should Find a Product by category"""
        products_by_category = {}
        products = ProductFactory.create_batch(15)
        for product in products:
            product.create()
            products_in_category = products_by_category.get(product.category, [])
            products_in_category.append(product)
            products_by_category[product.category] = products_in_category
        
        for category, products in products_by_category.items():
            found = Product.find_by_category(category)
            self.assertEqual(len(products), found.count())
