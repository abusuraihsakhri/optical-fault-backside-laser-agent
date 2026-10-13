"use strict";

const PRIMARY_BOUND = 25;
const SECONDARY_BOUND = 12;
const ANOMALY_TERMS = ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"];

function validatePayload(payload) {
  for (const key of ["task_id", "target_identifier", "status_descriptor"]) {
    if (typeof payload[key] !== "string" || !payload[key].trim() || payload[key].length > 128) {
      throw new Error(key + " must be nonempty and at most 128 characters.");
    }
  }
  for (const key of ["primary_metric", "secondary_metric"]) {
    if (typeof payload[key] !== "number" || !Number.isFinite(payload[key])) {
      throw new Error(key + " must be a finite number.");
    }
  }
  if (typeof payload.is_critical_flag !== "boolean") {
    throw new Error("is_critical_flag must be a boolean.");
  }
  return payload;
}

function classify(payload) {
  validatePayload(payload);
  const alerts = [];
  function alert(origin_worker, urgency, summary, technical_details) {
    alerts.push({origin_worker, urgency, summary, technical_details});
  }
  if (payload.primary_metric > PRIMARY_BOUND) {
    alert("InvariantQCWorker", "ELEVATED_RISK", "Primary metric threshold exceeded",
      "Primary value " + payload.primary_metric + " exceeds the demonstration bound " + PRIMARY_BOUND + ".");
  }
  if (payload.is_critical_flag || payload.secondary_metric > SECONDARY_BOUND) {
    alert("SafetyEscalationWorker", payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      "Safety threshold or critical flag triggered",
      "Secondary value: " + payload.secondary_metric + "; critical flag: " + payload.is_critical_flag + ".");
  }
  if (ANOMALY_TERMS.some(term => payload.status_descriptor.toUpperCase().includes(term))) {
    alert("ProtocolConformanceWorker", "ELEVATED_RISK", "Status descriptor marked anomalous",
      "A matching software anomaly descriptor was detected.");
  }
  const critical = alerts.filter(item => item.urgency === "CRITICAL_STAT_PANIC").length;
  const overall = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    mode: "local_rule_based_demo",
    task_id: payload.task_id,
    target_identifier: payload.target_identifier,
    overall_urgency: overall,
    integrity_status: critical ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: critical,
    alerts,
    consensus_summary: "Rule-based evaluation completed across three independent checks."
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {validatePayload, classify};
}

if (typeof document !== "undefined") {
  const $ = id => document.getElementById(id);
  let tasks = 0;
  let lastResult = null;

  function fieldPayload() {
    return {
      task_id: $("task_id").value.trim(),
      target_identifier: $("target_identifier").value.trim(),
      primary_metric: Number($("primary_metric").value),
      secondary_metric: Number($("secondary_metric").value),
      status_descriptor: $("status_descriptor").value.trim(),
      is_critical_flag: $("is_critical_flag").checked
    };
  }

  $("audit-form").addEventListener("submit", async event => {
    event.preventDefault();
    $("error").textContent = "";
    const run = $("run");
    run.disabled = true;
    try {
      const payload = validatePayload(fieldPayload());
      let result;
      if ($("mode").value === "server") {
        const response = await fetch("./api/audit", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload)
        });
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(body.detail ? JSON.stringify(body.detail) : "API returned HTTP " + response.status);
        }
        result = await response.json();
      } else {
        result = classify(payload);
      }
      lastResult = result;
      tasks += 1;
      $("count").textContent = String(tasks);
      $("warning-count").textContent = String(result.total_alerts - result.critical_alerts_count);
      $("critical-count").textContent = String(result.critical_alerts_count);
      $("result-summary").textContent = "Overall urgency: " + result.overall_urgency + " • " + result.integrity_status;
      $("alert-list").replaceChildren();
      for (const item of result.alerts) {
        const li = document.createElement("li");
        li.textContent = item.origin_worker + " — " + item.summary + " (" + item.urgency + ")";
        $("alert-list").append(li);
      }
      if (!result.alerts.length) {
        const li = document.createElement("li");
        li.textContent = "No thresholds exceeded.";
        $("alert-list").append(li);
      }
      $("result-json").textContent = JSON.stringify(result, null, 2);
      $("download").disabled = false;
    } catch (error) {
      $("error").textContent = error.message || "Unable to evaluate input.";
    } finally {
      run.disabled = false;
    }
  });

  $("download").addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "optical-fault-evaluation.json";
    anchor.click();
    URL.revokeObjectURL(url);
  });
}
