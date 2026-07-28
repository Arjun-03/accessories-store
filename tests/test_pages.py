def test_home_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Handmade Press-On Nails" in response.text


def test_product_list_page_shows_products(client, sample_product):
    response = client.get("/products")

    assert response.status_code == 200
    assert "Rose Gold Almond" in response.text


def test_product_detail_page_loads(client, sample_product):
    response = client.get("/products/rose-gold-almond")

    assert response.status_code == 200
    assert "Rose Gold Almond" in response.text


def test_product_detail_404_page(client):
    response = client.get("/products/does-not-exist")

    assert response.status_code == 404
    assert "Page not found" in response.text
