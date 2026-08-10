def test_admin_can_list_orders(admin_client, placed_order):
    response = admin_client.get("/admin/orders")
    assert response.status_code == 200
    assert placed_order.order_number in response.text


def test_admin_can_view_order_detail(admin_client, placed_order):
    response = admin_client.get(f"/admin/orders/{placed_order.order_number}")
    assert response.status_code == 200
    assert placed_order.customer_name in response.text


def test_admin_can_update_order_status(admin_client, placed_order):
    admin_client.post(
        f"/admin/orders/{placed_order.order_number}/status",
        data={"new_status": "processing"},
    )
    response = admin_client.get(f"/admin/orders/{placed_order.order_number}")
    assert "processing" in response.text


def test_invalid_status_is_rejected(admin_client, placed_order):
    response = admin_client.post(
        f"/admin/orders/{placed_order.order_number}/status",
        data={"new_status": "not_a_real_status"},
    )
    assert response.status_code == 400


def test_order_routes_block_anonymous(client, placed_order):
    # `client`, not `admin_client` — no login
    list_resp = client.get("/admin/orders", follow_redirects=False)
    detail_resp = client.get(f"/admin/orders/{placed_order.order_number}", follow_redirects=False)
    assert list_resp.status_code == 303
    assert detail_resp.status_code == 303
