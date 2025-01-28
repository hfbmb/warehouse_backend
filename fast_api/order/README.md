# Order Management API

The Order Management API is a FastAPI-based RESTful API for managing orders within a warehouse. It provides endpoints for creating, updating, and tracking orders, as well as user management.

## Table of Contents

- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## API Documentation

### Endpoints
    GET /orders/{order_id}/team: Retrieve a list of users assigned to a specific order.
    GET /orders/{order_id}/start: Start working on a specific order.
    GET /orders/: Retrieve a paginated list of all orders.
    GET /orders/{order_id}/info: Retrieve detailed information about a specific order.
    GET /orders/generate_url/: Generate a unique URL for salesmen to create orders.
    GET /orders/{order_id}/generate_url_update: Generate a unique URL for updating an existing order.
    GET /orders/{order_id}/unchecked_products: Retrieve a list of non-checked products in an order.
    POST /orders/: Create a new order and send an email confirmation to the client.
    PUT /orders/{order_id}: Update an existing order.
    PUT /orders/{order_id}/record: Allow a salesman to register an order.
    PUT /orders/{order_id}/invoice: Allow a manager to register an order.
    PUT /orders/{order_id}/approve: Approve or reject order products by a manager.
    PUT /orders/{order_id}/loader: Update the status of an order for loaders.

## Pagination 
    Pagination is implemented using the fastapi_pagination library to handle large result   sets.
## Usage
    Use the API endpoints to manage orders, users, and order-related tasks.
    Ensure that you have the necessary permissions and access rights based on your user role.
    Refer to the API documentation for detailed information on each endpoint, request/response formats, and example usage.

## Contributing
    Contributions are welcome! If you would like to contribute to this project, please follow these steps:
    Fork the repository.
    Create a new branch for your feature or bug fix.
    Make your changes and ensure they are well-tested.
    Submit a pull request with a clear description of your changes.