/**
 * antigravity-claw — JavaScript client SDK
 * https://github.com/deborahikssv/Antigravity-claw
 */

const DEFAULT_BASE_URL = "http://localhost:4242";

class AntigravityClawClient {
  /**
   * @param {string} baseUrl - Skill server URL (default: http://localhost:4242)
   */
  constructor(baseUrl = DEFAULT_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async #post(tool, params = {}) {
    const res = await fetch(`${this.baseUrl}/${tool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parameters: params }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(`antigravity-claw error [${res.status}]: ${err.error}`);
    }
    return res.json();
  }

  /** Fetch the OpenClaw skill manifest */
  async manifest() {
    const res = await fetch(`${this.baseUrl}/manifest`);
    return res.json();
  }

  /** Health check */
  async health() {
    const res = await fetch(`${this.baseUrl}/health`);
    return res.json();
  }

  /**
   * Compute antigravity lift force
   * @param {number} massKg
   * @param {number} altitudeM
   * @param {boolean} invert
   */
  async computeAntigravity(massKg, altitudeM, invert = true) {
    return this.#post("compute_antigravity", {
      mass_kg: massKg,
      altitude_m: altitudeM,
      invert,
    });
  }

  /**
   * Simulate levitation trajectory
   * @param {string} objectName
   * @param {number} massKg
   * @param {number} targetAltitudeM
   */
  async levitate(objectName, massKg, targetAltitudeM) {
    return this.#post("levitate", {
      object_name: objectName,
      mass_kg: massKg,
      target_altitude_m: targetAltitudeM,
    });
  }

  /** Get a random antigravity micro-poem */
  async poem() {
    return this.#post("antigravity_poem");
  }
}

// ── Node.js / ESM export ─────────────────────────────────────────────────────
if (typeof module !== "undefined") {
  module.exports = { AntigravityClawClient };
}
if (typeof window !== "undefined") {
  window.AntigravityClawClient = AntigravityClawClient;
}

export { AntigravityClawClient };
