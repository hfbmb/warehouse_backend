# Company Operations


## Retrieve Current User's Company
    Endpoint: /api/company/
    Method: GET
    Description: Retrieve the current user's company data.
    Authentication: Required
    Role Required: Director, Admin
    Response Format: JSON

## Create Company
    Endpoint: /api/company/
    Method: POST
    Description: Create a new company and register a founder.
    Authentication: Required
    Role Required: Director
    Request Format: JSON
    Response Format: JSON

## Update Company Data
    Endpoint: /api/company/
    Method: PUT
    Description: Update company data.
    Authentication: Required
    Role Required: Director, Admin
    Request Format: JSON
    Response Format: JSON

## Delete Company
    Endpoint: /api/company/
    Method: DELETE
    Description: Delete the current user's company and associated data.
    Authentication: Required
    Role Required: Director
    Response Format: JSON

# Warehouse Operations


## Retrieve Current User's Warehouse
    Endpoint: /api/warehouse/{warehouse_name}
    Method: GET
    Description: Retrieve the current user's warehouse data by name.
    Authentication: Required
    Role Required: Director, Manager, Admin
    Response Format: JSON

## Retrieve Warehouse Users
    Endpoint: /api/warehouse/users/
    Method: GET
    Description: Retrieve users associated with the current user's warehouse.
    Authentication: Required
    Role Required: Director, Admin, Manager
    Response Format: JSON (Paginated)

## Add Warehouse
    Endpoint: /api/warehouse/
    Method: POST
    Description: Add a new warehouse to the company.
    Authentication: Required
    Role Required: Director, Admin
    Request Format: JSON
    Response Format: JSON

## Create Warehouse Category
    Endpoint: /api/warehouse/create/category/{warehouse_name}
    Method: POST
    Description: Create a new category for a specific warehouse.
    Authentication: Required
    Role Required: Manager, Director, Admin
    Request Format: JSON
    Response Format: JSON

## Update Warehouse Data
    Endpoint: /api/warehouse/{warehouse_name}
    Method: PUT
    Description: Update warehouse data by name.
    Authentication: Required
    Role Required: Manager, Director, Admin
    Request Format: JSON
    Response Format: JSON

## Delete Warehouse
    Endpoint: /api/warehouse/{warehouse_name}
    Method: DELETE
    Description: Delete a warehouse by name and its associated data.
    Authentication: Required
    Role Required: Director, Admin
    Response Format: JSON

## Delete Warehouse Gate
    Endpoint: /api/warehouse/gates/{gate_name}
    Method: DELETE
    Description: Delete a gate by gate name.
    Authentication: Required
    Role Required: Director, Manager, Admin
    Response Format: JSON

## Pagination
    @Pagination is supported for endpoints that return lists of items. The page and items_per_page parameters can be used to navigate through the results.
    Authentication and Roles

## Authentication is required for most endpoints.
    Role-based access control is implemented to restrict access to certain operations based on user roles (e.g., Director, Manager, Admin).