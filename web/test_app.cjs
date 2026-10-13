"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");
const {classify} = require("./app.js");
const base = {task_id:"T1",target_identifier:"KEY1",primary_metric:25,secondary_metric:12,status_descriptor:"NOMINAL",is_critical_flag:false};

test("threshold equality is nominal", () => {
  assert.equal(classify(base).overall_urgency, "ROUTINE");
});
test("independent primary and secondary checks", () => {
  const result = classify({...base,primary_metric:25.1,secondary_metric:12.1});
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
  assert.equal(result.total_alerts, 2);
});
test("explicit critical flag takes precedence", () => {
  const result = classify({...base,is_critical_flag:true,status_descriptor:"FAIL"});
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(result.critical_alerts_count, 1);
  assert.equal(result.total_alerts, 2);
});
test("non-finite and blank inputs are rejected", () => {
  assert.throws(()=>classify({...base,primary_metric:Infinity}), /finite/);
  assert.throws(()=>classify({...base,task_id:" "}), /nonempty/);
  assert.throws(()=>classify({...base,is_critical_flag:"False"}), /boolean/);
});
