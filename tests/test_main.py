import sys
import os

# Allow imports from the project root (one level up)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ─── Home Route ───────────────────────────────────────────────────────────────

class TestHomeRoute:
    def test_home_status_code(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_json(self):
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"

    def test_home_response_body(self):
        response = client.get("/")
        data = response.json()
        assert data["status"] == "alive"
        assert data["framework"] == "FastAPI on Lambda"

    def test_home_has_expected_keys(self):
        response = client.get("/")
        data = response.json()
        assert "status" in data
        assert "framework" in data


# ─── Items Route ──────────────────────────────────────────────────────────────

class TestItemsRoute:
    def test_get_item_status_code(self):
        response = client.get("/items/1")
        assert response.status_code == 200

    def test_get_item_returns_correct_id(self):
        response = client.get("/items/42")
        data = response.json()
        assert data["item_id"] == 42

    def test_get_item_response_structure(self):
        response = client.get("/items/7")
        data = response.json()
        assert "item_id" in data

    def test_get_item_large_id(self):
        response = client.get("/items/999999")
        assert response.status_code == 200
        assert response.json()["item_id"] == 999999

    def test_get_item_invalid_string_id(self):
        """Non-integer item_id should return 422 Unprocessable Entity."""
        response = client.get("/items/abc")
        assert response.status_code == 422

    def test_get_item_negative_id(self):
        """Negative integers are still valid integers — should return 200."""
        response = client.get("/items/-1")
        assert response.status_code == 200
        assert response.json()["item_id"] == -1

    def test_get_item_zero(self):
        response = client.get("/items/0")
        assert response.status_code == 200
        assert response.json()["item_id"] == 0


# ─── Sum Route ────────────────────────────────────────────────────────────────

class TestSumRoute:
    def test_sum_status_code(self):
        response = client.get("/sum?a=2&b=3")
        assert response.status_code == 200

    def test_sum_correct_result(self):
        response = client.get("/sum?a=4&b=6")
        assert response.json() == {"sum": 10}

    def test_sum_negative_numbers(self):
        response = client.get("/sum?a=-5&b=3")
        assert response.json() == {"sum": -2}

    def test_sum_zeros(self):
        response = client.get("/sum?a=0&b=0")
        assert response.json() == {"sum": 0}

    def test_sum_large_numbers(self):
        response = client.get("/sum?a=1000000&b=2000000")
        assert response.json() == {"sum": 3000000}

    def test_sum_missing_param_returns_422(self):
        """Omitting a required query param should return 422."""
        response = client.get("/sum?a=5")
        assert response.status_code == 422

    def test_sum_invalid_param_type_returns_422(self):
        """Non-integer query params should return 422."""
        response = client.get("/sum?a=foo&b=bar")
        assert response.status_code == 422


# ─── 404 / Unknown Routes ─────────────────────────────────────────────────────

class TestUnknownRoutes:
    def test_unknown_route_returns_404(self):
        response = client.get("/does-not-exist")
        assert response.status_code == 404

    def test_unknown_nested_route_returns_404(self):
        response = client.get("/items/1/extra")
        assert response.status_code == 404


# ─── HTTP Method Restrictions ─────────────────────────────────────────────────

class TestMethodRestrictions:
    def test_post_to_home_returns_405(self):
        response = client.post("/")
        assert response.status_code == 405

    def test_delete_to_home_returns_405(self):
        response = client.delete("/")
        assert response.status_code == 405

    def test_post_to_items_returns_405(self):
        response = client.post("/items/1")
        assert response.status_code == 405

    def test_put_to_items_returns_405(self):
        response = client.put("/items/1")
        assert response.status_code == 405


# ─── OpenAPI / Docs ───────────────────────────────────────────────────────────

class TestDocs:
    def test_openapi_schema_accessible(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_swagger_ui_accessible(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self):
        response = client.get("/redoc")
        assert response.status_code == 200