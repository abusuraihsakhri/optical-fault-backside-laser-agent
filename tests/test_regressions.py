"""Regression tests for input parsing, HMAC validation, and HTTP/UI integration."""
import math

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from cli import _parse_csv_boolean, main


def test_hmac_detects_content_mutation():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("tester", "audit", "DONE", {"task_id": "T-1"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "ALTERED"
    assert not trail.verify_integrity()


def test_hmac_detects_recomputed_link_without_secret():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("tester", "audit", "DONE", {"task_id": "T-1"})
    trail.log("tester", "audit", "DONE", {"task_id": "T-2"})
    trail.logs[1]["prev_hash"] = "spoofed"
    assert not trail.verify_integrity()


def test_exposed_audit_log_is_snapshot():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("tester", "audit", "DONE", {"task_id": "T-1"})
    copy = trail.get_trail()
    copy[0]["actor"] = "attacker"
    copy.clear()
    assert trail.verify_integrity()
    assert len(trail.get_trail()) == 1


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_reject_nonfinite_metrics(bad):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T-1", target_identifier="KEY", primary_metric=bad)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T-1", target_identifier="KEY", primary_metric=1, secondary_metric=bad)


@pytest.mark.parametrize(("text", "expected"), [
    ("False", False), ("0", False), ("", False), ("TRUE", True), ("1", True), ("yes", True),
])
def test_csv_boolean(text, expected):
    assert _parse_csv_boolean(text) is expected


def test_csv_boolean_malformed():
    with pytest.raises(ValueError):
        _parse_csv_boolean("perhaps")


def test_cli_batch_preserves_false_critical_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input.csv").write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "T1,KEY,10,2,False,NOMINAL\n", encoding="utf-8"
    )
    assert main(["batch", "-i", "input.csv", "-o", "output.csv"]) == 0
    result = (tmp_path / "output.csv").read_text(encoding="utf-8")
    assert "ROUTINE" in result
    assert "CRITICAL_STAT_PANIC" not in result


def test_http_api_and_static_ui():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/").status_code == 200
    assert "Optical Fault Telemetry" in client.get("/").text
    response = client.post("/api/audit", json={
        "task_id": "T-1", "target_identifier": "KEY", "primary_metric": 25,
        "secondary_metric": 12, "status_descriptor": "NOMINAL", "is_critical_flag": False,
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    rejected = client.post("/api/audit", json={
        "task_id": "T-2", "target_identifier": "KEY", "primary_metric": "NaN",
    })
    assert rejected.status_code == 422
    phi = client.post("/api/audit", json={
        "task_id": "MRN-123456", "target_identifier": "KEY", "primary_metric": 2,
    })
    assert phi.status_code == 400
