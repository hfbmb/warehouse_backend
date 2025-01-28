# User Management API

This FastAPI-based API provides various user-related endpoints for registration, login, and management. Below is a description of each function in the code.

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

- User registration with hashed password storage.
- User login with access token generation.
- User logout with access token removal.
- User password change functionality.
- User profile retrieval.
- Access token refresh using a refresh token.
- User data update (e.g., profile information).
- Role-based access control.
- Pagination for listing users.

## Endpoints


### Endpoint: Get All Users
- URL: `/users/`
- Method: GET
- Parameters: None
- Description: Retrieves a paginated list of all users.
- Access Control: Requires the user to have the role of 'director' or 'admin'.

### Endpoint: Get User by ID
- URL: `/users/{user_id}`
- Method: GET
- Parameters:
  - `user_id` (Path Parameter): The ID of the user to retrieve.
- Description: Gets the user's data by their ID.
- Access Control: Requires the user to have the role of 'director', 'admin', or 'manager'.

### Endpoint: Get Current User's Information
- URL: `/users/user/info`
- Method: GET
- Parameters: None
- Description: Retrieves the information of the currently authenticated user.
- Access Control: Requires the user to be authenticated.

### Endpoint: Register a New User
- URL: `/users/`
- Method: POST
- Parameters: JSON data for user registration.
- Description: Registers a new user and sends a verification code via email.
- Access Control: Requires the user to have the role of 'director', 'admin', or 'manager'.

### Endpoint: Confirm User Registration with Verification Code
- URL: `/users/{verification_code}`
- Method: PUT
- Parameters:
  - `verification_code` (Path Parameter): The verification code received via email.
  - `email` (Query Parameter): The email address of the user.
- Description: Confirms user registration using a verification code.
- Access Control: Public, but requires a valid verification code and email address.

### Endpoint: User Login
- URL: `/users/login`
- Method: POST
- Example in curl: 
    curl -X 'POST' \
    'http://warehouse-app-test.prometeochain.io/users/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username=manager%40mail.ru&password=manager&scope=&client_id=&client_secret='
- Parameters: 
    User's login credentials (username(email) and password).
- content-Type: application/x-www-form-urlencoded
- Description: Allows a user to log in, providing an access token and a refresh token.
- Access Control: Public, but the user must have a confirmed verification code.

### Endpoint: User Logout
- URL: `/users/logout`
- Method: POST
- Parameters: None
- Description: Logs out the user by removing the access token cookie.
- Access Control: Requires the user to be authenticated.

### Endpoint: Refresh Access Token
- URL: `/users/take/access_token/{refresh_token}`
- Method: POST
- Parameters:
  - `refresh_token` (Path Parameter): The refresh token to generate a new access token.
- Description: Refreshes the access token using a valid refresh token.
- Access Control: Public, but requires a valid refresh token.

### Endpoint: Delete User by ID
- URL: `/users/{user_id}`
- Method: DELETE
- Parameters:
  - `user_id` (Path Parameter): The ID of the user to delete.
- Description: Deletes a user by their ID.
- Access Control: Requires the user to have the role of 'director', 'admin', or 'manager', and managers cannot delete other managers.

### Endpoint: Change User's Password
- URL: `/users/password/change`
- Method: POST
- Parameters: User's current and new passwords.
- Description: Allows a user to change their password securely.
- Access Control: Requires valid user credentials and access control.

### Endpoint: Forgot Password (Placeholder)
- URL: `/users/password/forgot`
- Method: PUT
- Parameters: User's email address.
- Description: Sends a verification code via email to allow password reset.
- Access Control: Public.

### Endpoint: Change Password with Verification Code
- URL: `/users/verification/code`
- Method: PUT
- Parameters: User's email, verification code, and new password.
- Description: Allows a user to change their password using a verification code.
- Access Control: Public, but requires a valid verification code.


### Endpoint: Change Password with Verification Code
- URL: `/users/verification/code`
- Method: PUT
- Parameters: JSON data including email, verification code, and a new password.
- Description: Allows a user to change their password using a verification code received via email. The provided email and verification code must be valid for security reasons. If the email and verification code match, the user's password is updated with the new password provided in the request. The user's 'is_confirmed' status is set to 'True' to indicate successful verification.
- Access Control: Public, but requires a valid email and verification code for security.

### Endpoint: Update User Data by ID
- URL: `/users/{user_id}`
- Method: PUT
- Parameters:
  - `user_id` (Path Parameter): The ID of the user to update.
  - `user_data` (JSON Body): User data to update.
- Description: Allows an authorized user (with roles 'director', 'admin', or 'manager') to update user data. The 'user_data' parameter contains the updated user information. This function is useful for making changes to user profiles or other details.
- Access Control: Requires the user to have the role of 'director', 'admin', or 'manager'.


## Dependencies

This API uses various dependencies for user authentication, exception handling, and pagination. These dependencies are managed internally within the codebase.

## Exception Handling

The API handles exceptions related to unauthorized access, permission issues, non-existent data, and invalid IDs. It provides appropriate error responses for each scenario.

## Pagination

The API supports pagination for listing users. It uses the `fastapi-pagination` library to provide paginated responses.

## How to Use


To utilize this API, you can make HTTP requests to the specified endpoints based on your user role and permissions. Detailed information on request and response formats can be found in the codebase.

## Contributing

If you would like to contribute to the development of this API, please follow the guidelines outlined in the CONTRIBUTING.md file in the repository.

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.
