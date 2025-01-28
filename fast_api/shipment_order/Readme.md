# FastAPI Shipment Management API

The FastAPI Shipment Management API is designed to manage shipment orders within your application. It allows users with different roles to create, retrieve, update, and delete shipment orders, ensuring efficient order management.

## Table of Contents

- [Features](#features)
- [Endpoints](#endpoints)
- [Dependencies](#dependencies)
- [Exception Handling](#exception-handling)
- [Pagination](#pagination)
- [How to Use](#how-to-use)
- [Contributing](#contributing)
- [License](#license)

## Features

- Creation of shipment orders with client information.
- Retrieval of shipment orders based on user roles (manager or client).
- Access to shipment details by order ID.
- Deletion of shipment orders by user roles.
- Update of shipment order details.
- Role-based access control.

## Endpoints

### Create Shipment Order

- **Endpoint:** `/shipment`
- **Method:** POST
- **Description:** Allows users to create a shipment order, including client information.
- **Permissions:** Managers and clients.
- **Response:** A success message.

### Get All Shipment Orders

- **Endpoint:** `/shipment/orders`
- **Method:** GET
- **Description:** Retrieves a paginated list of all shipment orders based on user roles (manager or client).
- **Permissions:** Managers and clients.
- **Response:** A paginated list of shipment orders.

### Get Shipment Order by Order ID

- **Endpoint:** `/shipment/{order_id}/shipment`
- **Method:** GET
- **Description:** Retrieves detailed information about a shipment order by its unique ID.
- **Permissions:** All user roles.
- **Response:** JSON data containing shipment order details.

### Delete Shipment Order by Order ID

- **Endpoint:** `/shipment/{order_id}`
- **Method:** DELETE
- **Description:** Deletes a shipment order by its unique ID, based on user roles (manager or client).
- **Permissions:** Managers and clients.
- **Response:** A success message.

### Update Shipment Order

- **Endpoint:** `/shipment/{order_id}`
- **Method:** PUT
- **Description:** Updates shipment order details based on user roles (manager or client).
- **Permissions:** Managers and clients.
- **Response:** A success message.

## Dependencies

This API uses several dependencies for user authentication and exception handling, which are managed internally within the codebase.

## Exception Handling

The API handles exceptions related to unauthorized access, permission issues, and data retrieval errors, providing appropriate error responses for each scenario.

## Pagination

The API supports pagination for listing shipment orders. It uses the `fastapi-pagination` library to provide paginated responses.

## How to Use

To utilize this API, make HTTP requests to the specified endpoints based on your user role and permissions. Detailed information on request and response formats can be found in the codebase.

## Contributing

If you'd like to contribute to the development of this API, please follow the guidelines outlined in the CONTRIBUTING.md file in the repository.

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.
