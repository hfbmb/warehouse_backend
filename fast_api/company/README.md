# Company API Documentation

## Overview

This API focuses on company-related operations, such as managing company details, employees, and other related functionalities. It's built using FastAPI and integrates with MongoDB for data storage.

## Directory Structure

- `constants.py`: Contains constant variables and enums used throughout the company module.
- `exception.py`: Defines custom exceptions specific to company operations.
- `models.py`: Contains the data models related to companies.
- `router.py`: Defines the API endpoints related to companies.
- `service.py`: Contains the core business logic for company operations.
- `test_company_service.py`: Unit tests for the service layer.
- `README.md`: This documentation file.
- `__init__.py`: Initialization file for the company module.
- `__pycache__`: Compiled Python files (automatically generated).



# Company API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Dependencies](#dependencies)
3. [API Endpoints](#api-endpoints)
    - [Get Current Company](#get-current-company)
    - [Create Company](#create-company)
    - [Update Company Data](#update-company-data)
    - [Delete Company](#delete-company)
4. [Pagination](#pagination)

## Overview

The `company` module focuses on operations related to managing companies. It provides API endpoints for creating, updating, deleting, and fetching company information. The module is built using FastAPI and integrates with various services and models.

## Dependencies

- FastAPI: For creating the API.
- FastAPI Pagination: For paginating lists of items.
- Logging: For logging errors and other information.

## API Endpoints

### Get Current Company

#### Endpoint Details

- **URL**: `/`
- **HTTP Method**: `GET`
- **Response Model**: `ReturnCompany`
- **Parameters**: None
- **Dependencies**: `get_current_user`
- **Exceptions**: `UnauthorizedException`, `PermissionException`

#### Code Explanation

- **`user_has_permission`**: This function checks if the current user has the permission to view their own company. It queries the database to verify the user's role and company.
  
- **`service.get_company`**: This function fetches the current user's company data from the database and returns it.

### Create Company

#### Endpoint Details

- **URL**: `/`
- **HTTP Method**: `POST`
- **Response Model**: `Success`
- **Parameters**: 
  - `founder`: An object of type `WebFounder` containing the founder's details.
  - `company`: An object of type `Company` containing the company details.
- **Exceptions**: `DuplicateKeyException`

#### Code Explanation

- **`check_founder_exists`**: This function checks if a founder with the given email already exists in the database. If so, it raises an exception.

- **`service.check_company_exists`**: This function checks if a company with the given name already exists in the database. If so, it raises an exception.

- **`register_founder`**: This function registers the founder in the database. It hashes the password and sets the role to `director`.

- **`service.create_company_`**: This function creates the company in the database. It sets the company status to `active`.

### Update Company Data

#### Endpoint Details

- **URL**: `/`
- **HTTP Method**: `PUT`
- **Response Model**: `Success`
- **Parameters**: 
  - `data`: An object of type `UpdateCompany` containing the updated company details.
- **Dependencies**: `get_current_user`
- **Exceptions**: `UnauthorizedException`, `PermissionException`

#### Code Explanation

- **`user_has_permission`**: This function checks if the current user has the permission to update the company data. It queries the database to verify the user's role and company.

- **`service.update_data`**: This function updates the company data in the database. It filters out null or empty values before updating.

### Delete Company

#### Endpoint Details

- **URL**: `/`
- **HTTP Method**: `DELETE`
- **Response Model**: None
- **Parameters**: None
- **Dependencies**: `get_current_user`

#### Code Explanation

- **`user_has_permission`**: This function checks if the current user has the permission to delete the company. It queries the database to verify the user's role and company.

- **`service.delete_company`**: This function deletes the company from the database.

- **`remove_all_user_in_company`**: This function removes all users associated with the company from the database.

- **`remove_all_orders_in_company`**: This function removes all orders associated with the company from the database.

- **`remove_all_products_in_company`**: This function removes all products associated with the company from the database.

## Pagination

The API uses FastAPI Pagination for paginating lists of items. The `add_pagination` function is added to the router to enable this feature.


## Additional Notes

- The `service.py` file contains the core logic for CRUD operations related to companies. It interacts with the database and performs validations.
- The `router.py` file defines the API endpoints and handles HTTP requests and responses.
