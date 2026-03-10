#!/usr/bin/env python3
"""
antigravity-claw — OpenClaw skill server
Inspired by https://antigravity.google/
"""

import json
import sys
import os
import math
import random
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

VERSION = "1.0.0"
PORT = int(os.environ.get("ANTIGRAVITY_PORT", 4242))

# ── Physics engine ──────────────────────────────────────────────────────────

GRAVITY_CONSTANT = 9.80665  # m/s²

def compute_antigravity(mass_kg: float, altitude_m: float, invert: bool = True) -> dict:
    """
    Compute antigravity lift force.
    F = m * g * altitude_factor
    """
    altitude_factor = 1 + (altitude_m / 6_371_000)  # Earth radius
    g = -GRAVITY_CONSTANT if invert else GRAVITY_CONSTANT
    force_n = mass_kg * g * altitude_factor
    energy_j = abs(force_n) * altitude_m
    return {
        "mass_kg": mass_kg,
        "altitude_m": altitude_m,
        "force_newtons": round(force_n, 4),
        "energy_joules": round(energy_j, 4),
        "inverted": invert,
        "escape_velocity_ms": round(math.sqrt(2 * GRAVITY_CONSTANT * altitude_m), 4) if altitude_m > 0 else 0.0,
    }


def levitate(object_name: str, mass_kg: float, target_altitude_m: float) -> dict:
    """Simulate levitation trajectory."""
    steps = 10
    trajectory = []
    for i in range(steps + 1):
        t = i / steps
        h = target_altitude_m * (3 * t**2 - 2 * t**3)  # smooth-step
        v = target_altitude_m * 6 * t * (1 - t)        # velocity
        trajectory.append({"t": round(t, 2), "altitude_m": round(h, 2), "velocity_ms": round(v, 2)})

    physics = compute_antigravity(mass_kg, target_altitude_m)
    return {
        "object": object_name,
        "target_altitude_m": target_altitude_m,
        "trajectory": trajectory,
        "physics": physics,
        "status": "levitating 🚀",
    }


def antigravity_poem() -> str:
    """Return a random antigravity-themed micro-poem."""
    poems = [
        "What goes up / need not come down / when you rewire the rules.",
        "Gravity is just / a suggestion / we politely declined.",
        "Up is a direction. / So is further up. / And beyond that: freedom.",
        "The apple fell. / Newton wrote it down. / We deleted the file.",
        "Roots hold trees. / Nothing holds you. / Fly.",
    ]
    return random.choice(poems)


# ── OpenClaw skill manifest ──────────────────────────────────────────────────

SKILL_MANIFEST = {
    "name": "antigravity-claw",
    "version": VERSION,
    "description": "Defying gravity through computation. Physics simulations, levitation trajectories, and antigravity poetry — all in one OpenClaw skill.",
    "author": "antigravity-claw contributors",
    "homepage": "https://github.com/deborahikssv/Antigravity-claw",
    "tools": [
        {
            "name": "compute_antigravity",
            "description": "Calculate antigravity lift force for a given mass and altitude",
            "parameters": {
                "type": "object",
                "properties": {
                    "mass_kg": {"type": "number", "description": "Object mass in kilograms"},
                    "altitude_m": {"type": "number", "description": "Target altitude in meters"},
                    "invert": {"type": "boolean", "description": "Invert gravity (default: true)", "default": True},
                },
                "required": ["mass_kg", "altitude_m"],
            },
        },
        {
            "name": "levitate",
            "description": "Simulate a smooth levitation trajectory for any object",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the object to levitate"},
                    "mass_kg": {"type": "number", "description": "Object mass in kilograms"},
                    "target_altitude_m": {"type": "number", "description": "Desired final altitude in meters"},
                },
                "required": ["object_name", "mass_kg", "target_altitude_m"],
            },
        },
        {
            "name": "antigravity_poem",
            "description": "Get an antigravity-themed micro-poem for creative inspiration",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    ],
}


# ── HTTP handler ─────────────────────────────────────────────────────────────

class SkillHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[antigravity-claw] {self.address_string()} — {format % args}", file=sys.stderr)

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/manifest":
            self.send_json(SKILL_MANIFEST)
        elif parsed.path == "/health":
            self.send_json({"status": "ok", "version": VERSION})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON"}, 400)
            return

        tool = parsed.path.lstrip("/")
        params = payload.get("parameters", payload)

        if tool == "compute_antigravity":
            result = compute_antigravity(
                mass_kg=float(params.get("mass_kg", 1.0)),
                altitude_m=float(params.get("altitude_m", 100.0)),
                invert=bool(params.get("invert", True)),
            )
            self.send_json(result)

        elif tool == "levitate":
            result = levitate(
                object_name=str(params.get("object_name", "unnamed object")),
                mass_kg=float(params.get("mass_kg", 1.0)),
                target_altitude_m=float(params.get("target_altitude_m", 100.0)),
            )
            self.send_json(result)

        elif tool == "antigravity_poem":
            self.send_json({"poem": antigravity_poem()})

        else:
            self.send_json({"error": f"Unknown tool: {tool}"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    print(f"""
  ▄▀█ █▄░█ ▀█▀ █ █▀▀ █▀█ ▄▀█ █░█ █ ▀█▀ █▄█
  █▀█ █░▀█ ░█░ █ █▄█ █▀▄ █▀█ ▀▄▀ █ ░█░ ░█░
  ░░░░░░░░░ █▀▀ █░░ ▄▀█ █░█░░░░░░░
  ░░░░░░░░░ █▄▄ █▄▄ █▀█ ▀▄▀░░░░░░░

  OpenClaw Skill  •  v{VERSION}
  Listening on http://localhost:{PORT}
  """)
    server = HTTPServer(("0.0.0.0", PORT), SkillHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[antigravity-claw] Server stopped.")


if __name__ == "__main__":
    main()
