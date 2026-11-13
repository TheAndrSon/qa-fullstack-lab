import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SHOP_DB", str(tmp_path / "shopsphere-test.db"))
    from fastapi.testclient import TestClient

    from apps.shopsphere.main import app

    with TestClient(app) as test_client:
        yield test_client
