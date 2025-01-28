# FastAPI Reports Management API

The FastAPI Reports Management API is designed to manage various reports and tasks within your application. It includes functionality for quality checks, product allocations, unsuitable places, and more. Different user roles, including controllers, warehouse managers, dispatchers, and others, can interact with this API to perform their tasks efficiently.

## Table of Contents

- [Features](#features)
- [Endpoints](#endpoints)
- [Dependencies](#dependencies)
- [Exception Handling](#exception-handling)
- [How to Use](#how-to-use)
- [Contributing](#contributing)
- [License](#license)

## Features

- Quality checks for products, managed by controllers.
- Allocation of products in the warehouse.
- Management of unsuitable places for products.
- Dispatcher reports for order-related tasks.
- Task reports for various user roles.
- User permissions and role-based access control.

## Endpoints

### Quality Check for Products (Controller)

- **Endpoint:** `PUT /reports/{product_id}/check_quality`
- **Method:** PUT
- **Description:** Allows controllers to perform quality checks on products.
- **Permissions:** Controller role.
- **Response:** A success message.

### Allocation of Products in the Warehouse (Warehouseman)

- **Endpoint:** `PUT /reports/{product_id}/allocate_warehouse`
- **Method:** PUT
- **Description:** Warehouseman allocates products in the warehouse.
- **Permissions:** Warehouseman role.
- **Response:** A success message.

### Confirmation of Product Location (Loader)

- **Endpoint:** `PUT /reports/{product_id}/confirm_location`
- **Method:** PUT
- **Description:** Loader confirms the location of a product.
- **Permissions:** Loader role.
- **Response:** A success message.

### Product Arrival (Warehouseman)

- **Endpoint:** `POST /reports/arrival_date`
- **Method:** POST
- **Description:** Warehouseman records the arrival date of a product.
- **Permissions:** Warehouseman role.
- **Response:** A success message.

### Return Products to Suppliers

- **Endpoint:** `PUT /reports/{product_id}/return_suppliers`
- **Method:** PUT
- **Description:** Allows managers to return products to suppliers.
- **Permissions:** Manager role.
- **Response:** A success message.

### Send Products to Customers

- **Endpoint:** `PUT /reports/{product_id}/send_to_customer`
- **Method:** PUT
- **Description:** Allows managers, controllers, and warehousemen to send products to customers.
- **Permissions:** Manager, Controller, Warehouseman roles.
- **Response:** A success message.

### Create Dispatcher Report

- **Endpoint:** `PUT /reports/{order_id}/check_documents`
- **Method:** PUT
- **Description:** Dispatchers create reports for order-related tasks.
- **Permissions:** Dispatcher role.
- **Response:** A success message.

### Unsuitable Places Management

- **Endpoint:** `POST /reports/unsuitable_place`
- **Method:** POST
- **Description:** Warehouseman records unsuitable places for products.
- **Permissions:** Warehouseman role.
- **Response:** A success message.

### Get All Unsuitable Places

- **Endpoint:** `GET /reports/`
- **Method:** GET
- **Description:** Retrieves a list of all unsuitable places.
- **Permissions:** Manager role.
- **Response:** A list of unsuitable places.

### Get Unsuitable Place by ID

- **Endpoint:** `GET /reports/{place_id}/place`
- **Method:** GET
- **Description:** Retrieves detailed information about an unsuitable place by its ID.
- **Permissions:** Manager role.
- **Response:** JSON data containing unsuitable place details.

### Invoice Products from Unsuitable Place

- **Endpoint:** `PUT /reports/invoice_unsuitable_place`
- **Method:** PUT
- **Description:** Managers invoice products from an unsuitable place.
- **Permissions:** Manager role.
- **Response:** A success message.

### Report Every Employee Task

- **Endpoint:** `PUT /reports/{order_id}/done_task`
- **Method:** PUT
- **Description:** Various user roles can report tasks related to an order.
- **Permissions:** Various roles.
- **Response:** A success message.

## Dependencies

This API uses various dependencies for file handling, user authentication, and exception handling, which are managed internally within the codebase.

## Exception Handling

The API handles exceptions related to unauthorized access, permission issues, data validation, and more, providing appropriate error responses for each scenario.

## How to Use

To utilize this API, make HTTP requests to the specified endpoints based on your user role and permissions. Detailed information on request and response formats can be found in the codebase.

## Contributing

If you'd like to contribute to the development of this API, please follow the guidelines outlined in the CONTRIBUTING.md file in the repository.

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.
