"""
MediStock Backend — Medicine Tests
"""


def test_create_and_list_category(client, admin_headers):
    # Create category
    response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": "Antibiotics", "description": "Antibacterial medications"},
    )
    assert response.status_code == 201
    cat_id = response.json()["data"]["id"]

    # List categories
    response = client.get("/api/v1/categories", headers=admin_headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert any(c["id"] == cat_id for c in items)


def test_create_and_get_medicine(client, admin_headers):
    # Create category first
    cat_res = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": "Pain Relief", "description": "Analgesics"},
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["data"]["id"]

    # Create medicine
    med_res = client.post(
        "/api/v1/medicines",
        headers=admin_headers,
        json={
            "name": "Paracetamol 500mg",
            "generic_name": "Acetaminophen",
            "category_id": cat_id,
            "dosage_form": "Tablet",
            "strength": "500mg",
            "unit": "tablet",
            "reorder_level": 50,
        },
    )
    assert med_res.status_code == 201
    med_id = med_res.json()["data"]["id"]

    # Get medicine by ID
    get_res = client.get(f"/api/v1/medicines/{med_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == "Paracetamol 500mg"
