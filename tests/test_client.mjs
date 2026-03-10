/**
 * tests/test_client.mjs
 * Basic smoke tests for antigravity-claw skill server
 * Run: node tests/test_client.mjs   (server must be running on port 4242)
 */

import { AntigravityClawClient } from "../src/client.js";

const client = new AntigravityClawClient();
let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    console.log(`  ✓  ${name}`);
    passed++;
  } catch (e) {
    console.error(`  ✗  ${name}\n     ${e.message}`);
    failed++;
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || "Assertion failed");
}

console.log("\n🧪 antigravity-claw test suite\n");

await test("health check returns ok", async () => {
  const h = await client.health();
  assert(h.status === "ok", `Expected status ok, got ${h.status}`);
});

await test("manifest lists 3 tools", async () => {
  const m = await client.manifest();
  assert(m.tools.length === 3, `Expected 3 tools, got ${m.tools.length}`);
});

await test("computeAntigravity returns negative force when inverted", async () => {
  const r = await client.computeAntigravity(10, 100, true);
  assert(r.force_newtons < 0, "Force should be negative when inverted");
  assert(typeof r.energy_joules === "number");
});

await test("levitate returns trajectory with 11 steps", async () => {
  const r = await client.levitate("coffee mug", 0.3, 50);
  assert(r.trajectory.length === 11, `Expected 11 steps, got ${r.trajectory.length}`);
  assert(r.status.includes("levitat"));
});

await test("poem returns a non-empty string", async () => {
  const r = await client.poem();
  assert(typeof r.poem === "string" && r.poem.length > 5);
});

console.log(`\n  Results: ${passed} passed, ${failed} failed\n`);
if (failed > 0) process.exit(1);
