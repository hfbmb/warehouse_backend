from fastapi.testclient import TestClient
from fast_api.main import app  # Adjust the import as needed.
from fast_api.user.models import DBUser  # Adjust the import.

client = TestClient(app)

def test_get_all_users_not_logged_in():
    response = client.get("/users/")
    assert response.status_code == 401  # 401 Unauthorized

def test_get_all_users_no_permission(mocked_service, mocker):
    # Mocking required dependencies
    mocker.patch("path.to.get_current_user", return_value=DBUser(role="some_role", company="some_company"))
    mocker.patch("path.to.user_has_permission", side_effect=PermissionException)

    response = client.get("/users/")
    assert response.status_code == 403  # 403 Forbidden

def test_get_all_users_with_permission(mocked_service, mocker):
    # Mocking required dependencies
    user_data = [DBUser(role="role1", company="company1"), DBUser(role="role2", company="company1")]
    mocker.patch("path.to.get_current_user", return_value=DBUser(role="some_role", company="some_company"))
    mocker.patch("path.to.user_has_permission", return_value=True)
    mocker.patch("path.to.service.get_all_users_by_company", return_value=user_data)

    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == len(user_data)
