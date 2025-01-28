# User Module Documentation

## File Structure

```
user/
├── config.py
├── constants.py
├── exception.py
├── __init__.py
├── models.py
├── permission_router.py
├── Readme.md
├── roles_router.py
├── router.py
├── service.py
└── utils.py
```

### File Explanations

- `config.py`: Contains configuration settings specific to the user module, such as constants and environment variables.
  
- `constants.py`: Defines constant values that are used throughout the user module, such as role names and permission levels.

- `exception.py`: Custom exception classes that handle specific errors related to user operations.

- `__init__.py`: Initialization file for the user module, making it a Python package.

- `models.py`: Defines the data models related to users, such as the User schema for the database.

- `permission_router.py`: Contains API endpoints related to user permissions, like assigning and revoking permissions.

- `roles_router.py`: Contains API endpoints related to user roles, like creating and deleting roles.

- `router.py`: The main router that includes all the API endpoints related to user operations like registration, login, and profile management.

- `service.py`: Service layer containing the business logic for user operations, called by the API endpoints in `router.py`.

- `utils.py`: Utility functions that are used across the user module, such as password hashing and token generation.

## User Module API Endpoints

(Include the API documentation here, explaining each endpoint, the HTTP methods, parameters, and what each endpoint does.)

# API Endpoints router.py 

Certainly, let's document the API endpoints in the `user` module based on the `router.py` file. This documentation will provide an overview of each API endpoint, its purpose, parameters, and code explanations.

### Get All Users

- **Endpoint**: `/users/`
- **Method**: `GET`
- **Response Model**: `Page[UserWithID]`
- **Description**: Retrieves a paginated list of all users based on the role of the current user.
- **Parameters**: 
  - `user` (DBUser): The current authenticated user.

#### Code Explanation
- `user_has_permission`: Checks if the user has the permission `view_all_users`.
- `service.get_all_users_by_company`: Fetches all users belonging to the same company as the current user.

### Get User by ID

- **Endpoint**: `/users/{user_id}`
- **Method**: `GET`
- **Response Model**: `dict`
- **Description**: Retrieves a specific user by their ID.
- **Parameters**: 
  - `user_id` (str): The ID of the user.
  - `current_user` (DBUser): The current authenticated user.

#### Code Explanation
- `user_has_permission`: Checks if the user has the permission `view_user_by_id`.
- `service.get_user_by`: Fetches the user by their ID.

### Register User

- **Endpoint**: `/users/`
- **Method**: `POST`
- **Response Model**: `Success`
- **Description**: Registers a new user.
- **Parameters**: 
  - `request` (WebUser): The data for the new user.
  - `current_user` (DBUser): The current authenticated user.

#### Code Explanation
- `user_has_permission`: Checks if the user has the permission `register_user`.
- `service.register_user_`: Registers the new user in the database.
- `send_email_to_client`: Sends a verification email to the new user.

### Confirm Verification Code

- **Endpoint**: `/users/{verification_code}`
- **Method**: `PUT`
- **Response Model**: `dict`
- **Description**: Confirms the verification code sent to the user's email.
- **Parameters**: 
  - `verification_code` (str): The verification code.
  - `email` (str): The email of the user.

#### Code Explanation
- `service.custom_get_user_info_get`: Fetches the user by their email and verification code.
- `service.update_user`: Updates the user's `is_confirmed` status.

### Login

- **Endpoint**: `/users/login`
- **Method**: `POST`
- **Response Model**: `dict`
- **Description**: Logs in a user.
- **Parameters**: 
  - `form_data` (OAuth2PasswordRequestForm): The login form data.

#### Code Explanation
- `service.get_user_by`: Fetches the user by their email.
- `utils.verify_password_exception`: Verifies the user's password.
- `utils.create_access_token`: Creates an access token for the user.

### Logout

- **Endpoint**: `/users/logout`
- **Method**: `POST`
- **Response Model**: `Success`
- **Description**: Logs out a user.
- **Parameters**: None

#### Code Explanation
- Deletes the `access_token` cookie.

### Delete User

- **Endpoint**: `/users/{user_id}`
- **Method**: `DELETE`
- **Response Model**: `Success`
- **Description**: Deletes a user by their ID.
- **Parameters**: 
  - `user_id` (str): The ID of the user.
  - `user` (DBUser): The current authenticated user.

#### Code Explanation
- `user_has_permission`: Checks if the user has the permission `delete_user`.
- `service.remove_user`: Deletes the user by their ID.

### Change Password

- **Endpoint**: `/users/password/change`
- **Method**: `POST`
- **Response Model**: `Success`
- **Description**: Changes the password of a user.
- **Parameters**: 
  - `user` (UserChangePassword): The data for changing the password.
  - `current_user` (DBUser): The current authenticated user.

#### Code Explanation
- `check_access_n_credentials`: Checks the user's credentials.
- `service.change_password_`: Changes the user's password in the database.

---

# API Endpoints role_router.py 


## Overview

The Role file is responsible for managing roles within the application. It provides API endpoints for creating, updating, deleting, and fetching roles.

## API Endpoints

### Create a New Role

- **Endpoint**: `/role/`
- **Method**: `POST`
- **Response Model**: `dict`
- **Description**: Creates a new role in the system.
- **Parameters**:
  - `data`: The data for the role in `Role` model format.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `create_role_for_users`: Service function that handles the logic for creating a new role in the database.

### Get All Roles

- **Endpoint**: `/role/`
- **Method**: `GET`
- **Response Model**: `Page[dict]`
- **Description**: Retrieves all roles based on the role of the current user.
- **Parameters**:
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `get_all_roles_in_company`: Service function that fetches all roles in a specific company.

### Get a Specific Role by ID

- **Endpoint**: `/role/{role_id}`
- **Method**: `GET`
- **Response Model**: `dict`
- **Description**: Retrieves a specific role by its ID.
- **Parameters**:
  - `role_id`: The ID of the role to retrieve.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `get_role_by_id`: Service function that fetches the role by its ID.

### Update a Role by ID

- **Endpoint**: `/role/{role_id}`
- **Method**: `PUT`
- **Response Model**: `dict`
- **Description**: Updates a specific role by its ID.
- **Parameters**:
  - `role_id`: The ID of the role to update.
  - `data`: The updated data for the role in `UpdateRole` model format.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `update_role_by_data`: Service function that updates the role data.

### Delete a Role by ID

- **Endpoint**: `/role/{role_id}`
- **Method**: `DELETE`
- **Response Model**: `dict`
- **Description**: Deletes a specific role by its ID.
- **Parameters**:
  - `role_id`: The ID of the role to delete.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `delete_role_by_id`: Service function that deletes the role by its ID.

---

Certainly, let's document the `permission` module in a `README.md` format to help developers understand its functionality and API endpoints.

---

# Api Endpoints permission_router.py

## Overview

The Permission file is responsible for managing permissions within the application. It provides API endpoints for creating, updating, deleting, and fetching permissions.

### Create a New Permission

- **Endpoint**: `/permission/`
- **Method**: `POST`
- **Response Model**: `dict`
- **Description**: Creates a new permission in the system.
- **Parameters**:
  - `data`: The data for the new permission in `Permission` model format.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `create_permission`: Service function that handles the logic for creating a new permission in the database.

### Get All Permissions

- **Endpoint**: `/permission/`
- **Method**: `GET`
- **Response Model**: `Page[dict]`
- **Description**: Retrieves all permissions.
- **Parameters**:
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `get_all_permission_data`: Service function that fetches all permissions.

### Get a Specific Permission by ID

- **Endpoint**: `/permission/{permission_id}`
- **Method**: `GET`
- **Response Model**: `dict`
- **Description**: Retrieves a specific permission by its ID.
- **Parameters**:
  - `permission_id`: The ID of the permission to retrieve.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `get_permission_by_id`: Service function that fetches the permission by its ID.

### Update a Permission by ID

- **Endpoint**: `/permission/{permission_id}`
- **Method**: `PUT`
- **Response Model**: `dict`
- **Description**: Updates a specific permission by its ID.
- **Parameters**:
  - `permission_id`: The ID of the permission to update.
  - `data`: The updated data for the permission in `UpdatePermission` model format.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `update_permission_by_id`: Service function that updates the permission data.

### Delete a Permission by ID

- **Endpoint**: `/permission/{permission_id}`
- **Method**: `DELETE`
- **Response Model**: `dict`
- **Description**: Deletes a specific permission by its ID.
- **Parameters**:
  - `permission_id`: The ID of the permission to delete.
  - `current_user`: The current user making the request, determined by the `get_current_user` dependency.

#### Code Explanation

- `delete_permission_by_id`: Service function that deletes the permission by its ID.

---

