# Product Management API

This API provides endpoints for managing products within your application. It allows users with different roles to access and manipulate product data.

## Endpoints

### Get Product by Client Email

- **Endpoint:** `/products/{client_email}`
- **Method:** GET
- **Description:** Retrieves product information based on a client's email.
- **Permissions:** All user roles.
- **Response:** JSON data containing product information.

### Generate QR Codes

- **Endpoint:** `/products/generate/qr`
- **Method:** GET
- **Description:** Generates QR codes.
- **Permissions:** All user roles.
- **Response:** A list of generated QR codes.

### Get All Products

- **Endpoint:** `/products/`
- **Method:** GET
- **Description:** Retrieves a paginated list of all products based on user role and permissions.
- **Permissions:** Authenticated users with appropriate roles.
- **Response:** A paginated list of product data.

### Get Products by Order ID

- **Endpoint:** `/products/get_products_by/{order_id}`
- **Method:** GET
- **Description:** Retrieves products for a specific order by order ID.
- **Permissions:** Authorized roles, including admin, controller, warehouseman, manager, and loader.
- **Response:** Detailed information about products for the specified order, including any missing goods.

### Get Product by Product ID

- **Endpoint:** `/products/{product_id}`
- **Method:** GET
- **Description:** Retrieves detailed information about a product by its unique ID.
- **Permissions:** Authenticated users with appropriate roles.
- **Response:** JSON data containing detailed product information.

### Relocate Product

- **Endpoint:** `/products/{product_id}/relocate`
- **Method:** PUT
- **Description:** Relocates a product to a new storage location.
- **Permissions:** Warehouseman and loader roles.
- **Response:** A success message.

### Get Product by Product Name

- **Endpoint:** `/products/product_by/{product_name}`
- **Method:** GET
- **Description:** Retrieves the total quantity of a product by its name.
- **Permissions:** All user roles.
- **Response:** JSON data containing the total quantity of the specified product.

## Dependencies

This API relies on several dependencies for user authentication, exception handling, and pagination. These dependencies are managed internally.

## Exception Handling

The API handles exceptions related to unauthorized access, permission issues, non-existent data, and invalid IDs. It provides appropriate error responses for each case.

## Pagination

The API supports pagination for listing products. It uses the `fastapi-pagination` library to provide paginated responses.

## How to Use

You can use this API to manage products within your application based on user roles and permissions. Make HTTP requests to the specified endpoints to interact with product data.

Please refer to the code for more detailed information on request and response formats.

