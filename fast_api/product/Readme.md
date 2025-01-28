# Product API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Dependencies](#dependencies)
4. [API Endpoints](#api-endpoints)
    - [Get Product by Client Email](#get-product-by-client-email)
    - [Generate QR Codes](#generate-qr-codes)
    - [Get All Products](#get-all-products)
    - [Get Products by Order ID](#get-products-by-order-id)
    - [Get Product by Product ID](#get-product-by-product-id)
    - [Relocate Product](#relocate-product)
    - [Get Product by Product Name](#get-product-by-product-name)
5. [Pagination](#pagination)

## Overview

The `product` module focuses on operations related to managing products. It provides API endpoints for creating, updating, deleting, and fetching product information. The module is built using FastAPI and integrates with various services and models.

## Directory Structure

```
product/
├── constants.py
├── exceptions.py
├── __init__.py
├── models.py
├── __pycache__
├── Readme.md
├── router.py
└── service.py
```

- `constants.py`: Contains all the constant values used in the product module.
- `exceptions.py`: Defines custom exceptions for the product module.
- `models.py`: Contains the data models related to products.
- `router.py`: Defines all the API endpoints related to products.
- `service.py`: Contains the business logic for handling product-related operations.


## Overview

The `product` module focuses on operations related to managing products. It provides API endpoints for creating, updating, deleting, and fetching product information. The module is built using FastAPI and integrates with various services and models.

## Dependencies

- FastAPI: For creating the API.
- FastAPI Pagination: For paginating lists of items.

## API Endpoints

### Get Product by Client Email

#### Endpoint Details

- **URL**: `/{client_email}`
- **HTTP Method**: `GET`
- **Response Model**: `dict`
- **Parameters**: 
  - `client_email`: The email of the client.

#### Code Explanation

- **`service.find_products_by_client_email`**: This function fetches the products associated with the given client email from the database.

### Generate QR Codes

#### Endpoint Details

- **URL**: `/generate/qr`
- **HTTP Method**: `GET`
- **Response Model**: `list`
- **Parameters**: 
  - `count`: The number of QR codes to generate.

#### Code Explanation

- **`generate_qr_code`**: This function generates the specified number of QR codes.

### Get All Products

#### Endpoint Details

- **URL**: `/`
- **HTTP Method**: `GET`
- **Response Model**: `Page[dict]`
- **Parameters**: None
- **Dependencies**: `get_current_user`
- **Exceptions**: `UnauthorizedException`, `PermissionException`

#### Code Explanation

- **`service.return_all_products`**: This function fetches all the products based on the user role and permissions.

### Get Products by Order ID

#### Endpoint Details

- **URL**: `/get_products_by/{order_id}`
- **HTTP Method**: `GET`
- **Response Model**: `dict`
- **Parameters**: 
  - `order_id`: The ID of the order.
- **Dependencies**: `get_current_user`

#### Code Explanation

- **`get_order_by_id`**: This function fetches the order data by its ID.
  
- **`service.return_all_products`**: This function fetches all the products associated with the given order ID.

### Get Product by Product ID

#### Endpoint Details

- **URL**: `/{product_id}`
- **HTTP Method**: `GET`
- **Response Model**: `dict`
- **Parameters**: 
  - `product_id`: The ID of the product.
- **Dependencies**: `get_current_user`
- **Exceptions**: `DoesNotExist`

#### Code Explanation

- **`service.get_product_by_id_`**: This function fetches the product data by its ID.

### Relocate Product

#### Endpoint Details

- **URL**: `/{product_id}/relocate`
- **HTTP Method**: `PUT`
- **Response Model**: `Success`
- **Parameters**: 
  - `product_id`: The ID of the product.
  - `location`: The new location for the product.
- **Dependencies**: `get_current_user`
- **Exceptions**: `UnauthorizedException`, `PermissionException`, `DoesNotExist`, `InvalidIdException`

#### Code Explanation

- **`service.update_product`**: This function updates the location of the product in the database.

### Get Product by Product Name

#### Endpoint Details

- **URL**: `/product_by/{product_name}`
- **HTTP Method**: `GET`
- **Response Model**: `dict`
- **Parameters**: 
  - `product_name`: The name of the product.
- **Dependencies**: `get_current_user`

#### Code Explanation

- **`service.get_total_quantity_product_by_name`**: This function fetches the total quantity of a product by its name.

## Pagination

The API uses FastAPI Pagination for paginating lists of items. The `add_pagination` function is added to the router to enable this feature.

