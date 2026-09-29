"""
MediStock Backend — Inventory & Sales Flow Tests
"""

from datetime import date, timedelta


def test_full_inventory_and_sales_flow(client, admin_headers):
    # 1. Create Supplier
    sup_res = client.post(
        "/api/v1/suppliers",
        headers=admin_headers,
        json={
            "name": "Global Pharma Supply",
            "contact_person": "Jane Doe",
            "email": "jane@globalpharma.com",
            "phone": "555-0199",
        },
    )
    assert sup_res.status_code == 201
    supplier_id = sup_res.json()["data"]["id"]

    # 2. Create Medicine Category & Medicine
    cat_res = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": "Cardiology", "description": "Heart medications"},
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["data"]["id"]

    med_res = client.post(
        "/api/v1/medicines",
        headers=admin_headers,
        json={
            "name": "Atorvastatin 20mg",
            "generic_name": "Atorvastatin",
            "category_id": cat_id,
            "dosage_form": "Tablet",
            "strength": "20mg",
            "unit": "tablet",
            "reorder_level": 20,
        },
    )
    assert med_res.status_code == 201
    medicine_id = med_res.json()["data"]["id"]

    # 3. Create and Receive Purchase Order (Stocks the pharmacy)
    future_date = (date.today() + timedelta(days=365)).isoformat()
    po_res = client.post(
        "/api/v1/purchases",
        headers=admin_headers,
        json={
            "supplier_id": supplier_id,
            "purchase_date": date.today().isoformat(),
            "items": [
                {
                    "medicine_id": medicine_id,
                    "quantity": 100,
                    "unit_cost": 1.50,
                }
            ],
            "notes": "Initial stock order",
        },
    )
    assert po_res.status_code == 201
    purchase_data = po_res.json()["data"]
    purchase_id = purchase_data["id"]
    purchase_item_id = purchase_data["items"][0]["id"]

    # Receive PO into batch
    receive_res = client.post(
        f"/api/v1/purchases/{purchase_id}/receive",
        headers=admin_headers,
        json={
            "items": [
                {
                    "purchase_item_id": purchase_item_id,
                    "quantity_received": 100,
                    "batch_number": "BATCH-ATO-001",
                    "manufacturing_date": date.today().isoformat(),
                    "expiry_date": future_date,
                    "selling_price": 3.00,
                }
            ]
        },
    )
    assert receive_res.status_code == 200

    # 4. Check Inventory
    inv_res = client.get("/api/v1/inventory", headers=admin_headers)
    assert inv_res.status_code == 200
    inv_items = inv_res.json()["data"]["items"]
    med_inv = next((i for i in inv_items if i["medicine_id"] == medicine_id), None)
    assert med_inv is not None
    assert med_inv["total_quantity"] == 100

    # 5. Execute Sale (FIFO Batch deduction)
    sale_res = client.post(
        "/api/v1/sales",
        headers=admin_headers,
        json={
            "customer_name": "Alice Smith",
            "sale_date": date.today().isoformat(),
            "payment_method": "CASH",
            "items": [
                {
                    "medicine_id": medicine_id,
                    "quantity": 10,
                }
            ],
        },
    )
    assert sale_res.status_code == 201
    sale_data = sale_res.json()["data"]
    assert sale_data["total_amount"] == 30.0  # 10 * 3.00
    assert sale_data["customer_name"] == "Alice Smith"

    # 6. Verify Remaining Stock is 90
    inv_res_after = client.get("/api/v1/inventory", headers=admin_headers)
    inv_items_after = inv_res_after.json()["data"]["items"]
    med_inv_after = next((i for i in inv_items_after if i["medicine_id"] == medicine_id), None)
    assert med_inv_after["total_quantity"] == 90

    # 7. Check Stock Movement Ledger
    movements_res = client.get("/api/v1/stock-movements", headers=admin_headers)
    assert movements_res.status_code == 200
    movements = movements_res.json()["data"]["items"]
    assert len(movements) >= 2  # 1 receipt (+100) and 1 sale (-10)
