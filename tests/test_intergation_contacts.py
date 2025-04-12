
from datetime import date


test_contact = {
    "name": "Tommy",
    "lastname": "Boss",
    "email": "user@gmail.com",
    "phone": "111111222222",
    "birthdate": "2025-04-10",
    "info": "some info",
}

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact_not_found(client, get_token):
    updated_test_contact = test_contact.copy()
    updated_test_contact["name"] = "New_name"

    response = client.patch(
        "/api/contact/2",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Not Found"


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
