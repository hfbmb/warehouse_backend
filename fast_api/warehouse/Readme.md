# Warehouse Management System

This Warehouse Management System is designed to manage different aspects of a warehouse, including categories, conditions, floors, racks, zones, and cells.

## Project Structure

- `category_router.py`: This module handles category-related functionality.
- `condition_router.py`: This module handles condition-related functionality.
- `constants.py`: Constants used throughout the project.
- `exceptions.py`: Custom exceptions used in the project.
- `floor_router.py`: This module handles floor-related functionality.
- `models.py`: Define the data models used in the project.
- `rack_router.py`: This module handles rack-related functionality.
- `zone_router.py`: This module handles zone-related functionality.
- `cells_router.py`: This module handles cell-related functionality.
- `router.py`: The main router module that ties everything together.
- `service.py`: Contains services used by the routers.
- `__init__.py`: Initialization file for the package.
- `__pycache__`: Cached Python files.


# Warehouse Management API

The FastAPI Warehouse Management API allows you to efficiently manage warehouse-related operations, including creating, retrieving, updating, and deleting warehouses and associated data. This API provides role-based access control and supports pagination for a smooth user experience.

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

- **Create Warehouses**: Add new warehouses to your company.
- **Retrieve Warehouse Data**: Get detailed information about a warehouse.
- **Retrieve Warehouse Users**: Retrieve and paginate a list of users associated with a specific warehouse.
- **Update Warehouse Data**: Modify warehouse information.
- **Delete Warehouses**: Remove a warehouse and associated users.
- **Role-Based Access Control**: Ensure that different user roles have appropriate access permissions.

## Endpoints

### Retrieve Current User's Warehouse

- **Endpoint:** `/warehouses/{warehouse_name}`
- **Method:** GET
- **Description:** Retrieves the current user's warehouse by warehouse name.
- **Permissions:** All user roles.
- **Response:** JSON data containing warehouse details.

### Retrieve Warehouse Users

- **Endpoint:** `/warehouses/users/`
- **Method:** GET
- **Description:** Retrieves and paginates a list of users associated with the current user's company and warehouse.
- **Permissions:** Directors, Admins, and Managers.
- **Response:** A paginated list of warehouse users.

### Add a New Warehouse

- **Endpoint:** `/warehouses/`
- **Method:** POST
- **Description:** Adds a new warehouse to the company using provided data.
- **Permissions:** Directors, Admins, and Managers.
- **Response:** A success message.

### Update Warehouse Data

- **Endpoint:** `/warehouses/{warehouse_name}`
- **Method:** PUT
- **Description:** Updates warehouse data by name or based on the current user's warehouse.
- **Permissions:** Managers, Directors, and Admins.
- **Response:** A success message.

### Delete a Warehouse

- **Endpoint:** `/warehouses/{warehouse_name}`
- **Method:** DELETE
- **Description:** Deletes a warehouse by name or the current user's warehouse.
- **Permissions:** Directors and Admins.
- **Response:** A success message.

### Delete a Gate by Gate Name

- **Endpoint:** `/warehouses/gates/{gate_name}`
- **Method:** DELETE
- **Description:** Deletes a gate by its name.
- **Permissions:** Directors, Managers, and Admins.
- **Response:** A success message.

## Dependencies

This API leverages several dependencies for user authentication, exception handling, and pagination management, which are seamlessly integrated into the codebase.

## Exception Handling

The API effectively handles exceptions related to unauthorized access, permission issues, and data retrieval errors, providing meaningful error responses for each situation.

## Pagination

For enhanced user experience, this API includes support for pagination when listing warehouse users, making it efficient even when dealing with large datasets. This functionality is achieved through the `fastapi-pagination` library.

## How to Use

To utilize this API, you can make HTTP requests to the specified endpoints based on your user role and permissions. Detailed information on request and response formats can be found in the codebase.

## Contributing

If you'd like to contribute to the development of this API, please follow the guidelines outlined in the CONTRIBUTING.md file in the repository.

## License

This project is licensed under the MIT License. Please refer to the LICENSE.md file for detailed information.