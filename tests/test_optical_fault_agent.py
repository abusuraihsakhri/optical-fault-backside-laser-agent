"""
Automated Pytest Test Suite for Optical Fault Backside Laser Agent Core Engine.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus, ConsensusDossier
from agents.supervisor import SystemSupervisor
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.base import PHIGuard, AuditLogger, SecurityException
from cli import main


def test_invariant_qc_worker():
    """Worker 1: Primary Mathematical & Protocol Boundary Auditor."""
    # Elevated case - primary metric exceeds threshold
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED
    assert alerts1[0].origin_worker == "InvariantQCWorker"

    # Routine case - within bounds
    p_routine = SystemTaskPayload(task_id="T1B", target_identifier="KEY-01B", primary_metric=10.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts_routine = InvariantQCWorker.evaluate(p_routine)
    assert len(alerts_routine) == 0


def test_safety_escalation_worker():
    """Worker 2: Safety Boundary, Toxicity & Emergency Interlock Worker."""
    # Critical case - is_critical_flag is True
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, secondary_metric=15.0, status_descriptor="NOMINAL", is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Elevated case - secondary metric exceeds threshold
    p_elev = SystemTaskPayload(task_id="T2B", target_identifier="KEY-02B", primary_metric=10.0, secondary_metric=13.0, status_descriptor="NOMINAL", is_critical_flag=False)
    alerts_elev = SafetyEscalationWorker.evaluate(p_elev)
    assert len(alerts_elev) == 1
    assert alerts_elev[0].urgency == UrgencyLevel.ELEVATED


def test_protocol_conformance_worker():
    """Worker 3: Spec Conformance, Anomaly Triage & Discordance Checker."""
    # Discordant descriptor triggers alert
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, secondary_metric=4.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1
    assert alerts3[0].origin_worker == "ProtocolConformanceWorker"

    # Nominal descriptor - no alert
    p_nominal = SystemTaskPayload(task_id="T3B", target_identifier="KEY-03B", primary_metric=10.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts_nominal = ProtocolConformanceWorker.evaluate(p_nominal)
    assert len(alerts_nominal) == 0


def test_supervisor_consensus():
    """Supervisor orchestrates multi-worker evaluation and produces consensus dossier."""
    supervisor = SystemSupervisor(model_provider="mock")

    # Nominal case - all workers agree on routine
    p_nominal = SystemTaskPayload(task_id="T4", target_identifier="KEY-04", primary_metric=12.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    dossier = supervisor.process_task(p_nominal)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.total_alerts == 0
    assert isinstance(dossier, ConsensusDossier)
    assert dossier.audit_hash != ""

    # Critical case - safety worker triggers critical
    p_critical = SystemTaskPayload(task_id="T5", target_identifier="KEY-05", primary_metric=30.0, secondary_metric=15.0, status_descriptor="DISCORDANT_ANOMALY", is_critical_flag=True)
    dossier_crit = supervisor.process_task(p_critical)
    assert dossier_crit.overall_urgency == UrgencyLevel.CRITICAL_STAT
    assert dossier_crit.integrity_status == SystemIntegrityStatus.RECALIBRATION_REQUIRED
    assert dossier_crit.total_alerts >= 3  # All three workers should fire


def test_phi_guard_blocks_sensitive_data():
    """PHI Guard must block outbound sensitive identifiers."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("SSN 123-45-6789 detected")

    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Contact patient at 555-123-4567")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
    PHIGuard.assert_no_phi("")


def test_audit_trail_integrity():
    """HMAC-SHA256 audit trail must maintain cryptographic chain integrity."""
    # Process a task to generate audit entries
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(task_id="AUDIT-01", target_identifier="KEY-AUDIT-01", primary_metric=15.0, secondary_metric=5.0, status_descriptor="NOMINAL")
    supervisor.process_task(payload)

    # Verify chain integrity
    assert AuditLogger.verify_integrity() is True
    trail = AuditLogger.get_trail()
    assert len(trail) > 0


def test_cli_audit_command():
    """CLI audit subcommand executes successfully."""
    assert main(["audit", "--task-id", "CLI-01"]) == 0
    assert main(["audit", "--task-id", "CLI-02", "--primary", "35.0", "--critical"]) == 0


def test_cli_chat_command():
    """CLI chat subcommand executes successfully."""
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_cli_verify_audit_command():
    """CLI verify-audit subcommand executes successfully."""
    assert main(["verify-audit"]) == 0


def test_phi_guard_in_supervisor():
    """Supervisor must reject payloads containing PHI in task_id."""
    supervisor = SystemSupervisor(model_provider="mock")
    phi_payload = SystemTaskPayload(
        task_id="Patient MRN-12345678",
        target_identifier="KEY-01",
        primary_metric=10.0,
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(phi_payload)
