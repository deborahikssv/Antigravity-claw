<div align="center">

<br />

```
  ▄▀█ █▄░█ ▀█▀ █ █▀▀ █▀█ ▄▀█ █░█ █ ▀█▀ █▄█
  █▀█ █░▀█ ░█░ █ █▄█ █▀▄ █▀█ ▀▄▀ █ ░█░ ░█░
  ░░░░ █▀▀ █░░ ▄▀█ █░█ ░░░░
  ░░░░ █▄▄ █▄▄ █▀█ ▀▄▀ ░░░░
```

**An OpenClaw skill that defies gravity — and expectations.**

[![CI](https://github.com/deborahikssv/Antigravity-claw/actions/workflows/ci.yml/badge.svg)](https://github.com/deborahikssv/Antigravity-claw/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-brightgreen)](https://python.org)
[![OpenClaw Skill](https://img.shields.io/badge/openclaw-skill-purple)](https://github.com/deborahikssv/Antigravity-claw)

<br />

*Inspired by [antigravity.google](https://antigravity.google/) — the one page that proved even gravity has a sense of humor.*

</div>

---

## What is antigravity-claw?

`antigravity-claw` is an **OpenClaw skill** that brings antigravity physics to your AI assistant.

Give your AI the ability to:
- 🧮 **Compute lift force** — real physics, inverted sign
- 🚀 **Simulate levitation trajectories** — smooth-step curves, velocity graphs, escape velocity
- 🪐 **Generate antigravity poetry** — because science needs a soul

One skill server. Three tools. Zero gravity.

---

## Install in one command

**macOS / Linux:**

```bash
curl -fsSLk https://github.com/deborahikssv/Antigravity-claw/archive/refs/heads/main.zip -o /tmp/cw.zip && \
unzip -qo /tmp/cw.zip -d /tmp && \
cd /tmp/Antigravity-claw-main && \
bash install.sh
```

**Already have the zip?**

```bash
unzip Antigravity-claw-main.zip
cd Antigravity-claw-main
bash install.sh
```

That's it. The installer will:
1. Verify your Python 3.9+ environment
2. Copy the skill to `~/.openclaw/skills/antigravity-claw/`
3. Create a launcher binary at `~/.local/bin/antigravity-claw`
4. Register the skill in your OpenClaw config
5. Run a live smoke test to confirm everything works

---

## Start the server

```bash
antigravity-claw
```

```
  ╔══════════════════════════════════════════╗
  ║   🚀  antigravity-claw  •  v1.0.0        ║
  ║   Listening on http://localhost:4242      ║
  ╚══════════════════════════════════════════╝
```

Custom port:

```bash
ANTIGRAVITY_PORT=9000 antigravity-claw
```

---

## Tools

Once the skill is running, your OpenClaw agent gets access to three tools:

### `compute_antigravity`

Calculate the lift force required to counteract gravity at a given altitude.

```json
POST /compute_antigravity
{
  "parameters": {
    "mass_kg": 70,
    "altitude_m": 10000,
    "invert": true
  }
}
```

```json
{
  "mass_kg": 70,
  "altitude_m": 10000,
  "force_newtons": -686.5647,
  "energy_joules": 6865647.0,
  "inverted": true,
  "escape_velocity_ms": 442.9447
}
```

---

### `levitate`

Simulate a smooth levitation trajectory from ground to target altitude — with velocity at each step.

```json
POST /levitate
{
  "parameters": {
    "object_name": "espresso machine",
    "mass_kg": 8.5,
    "target_altitude_m": 100
  }
}
```

```json
{
  "object": "espresso machine",
  "target_altitude_m": 100,
  "trajectory": [
    { "t": 0.0, "altitude_m": 0.0,   "velocity_ms": 0.0   },
    { "t": 0.1, "altitude_m": 2.8,   "velocity_ms": 54.0  },
    ...
    { "t": 1.0, "altitude_m": 100.0, "velocity_ms": 0.0   }
  ],
  "physics": { ... },
  "status": "levitating 🚀"
}
```

---

### `antigravity_poem`

Returns a random micro-poem. Because why not.

```json
POST /antigravity_poem
{}
```

```json
{
  "poem": "Gravity is just / a suggestion / we politely declined."
}
```

---

## JavaScript SDK

Use the built-in client in your own scripts or web apps:

```js
import { AntigravityClawClient } from "./src/client.js";

const ag = new AntigravityClawClient(); // default: http://localhost:4242

// Physics
const force = await ag.computeAntigravity(10, 500);
console.log(force.force_newtons); // -98.1...

// Trajectory
const flight = await ag.levitate("rubber duck", 0.05, 200);
console.log(flight.trajectory);

// Poetry
const { poem } = await ag.poem();
console.log(poem);
```

The client works in both **Node.js** and the **browser** (no bundler required).

---

## Manifest & health endpoints

| Endpoint       | Method | Description                          |
|----------------|--------|--------------------------------------|
| `/`            | GET    | OpenClaw skill manifest (JSON)       |
| `/manifest`    | GET    | Same as above                        |
| `/health`      | GET    | `{"status":"ok","version":"1.0.0"}`  |

---

## Run tests

**Python unit tests** (no server needed):

```bash
python -m pytest tests/test_server.py -v
```

**JavaScript integration tests** (server must be running):

```bash
node tests/test_client.mjs
```

---

## Project structure

```
antigravity-claw/
├── src/
│   ├── server.py       # Python skill server (stdlib only, no deps)
│   └── client.js       # JavaScript client SDK (ESM + CJS)
├── tests/
│   ├── test_server.py  # Python unit tests (pytest)
│   └── test_client.mjs # JS integration tests
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions CI
├── install.sh          # One-command installer
├── package.json
├── LICENSE
└── README.md
```

---

## Requirements

| Runtime    | Version |
|------------|---------|
| Python     | 3.9+    |
| Node.js    | 18+ (optional, for JS client / tests) |
| macOS / Linux | ✅ |
| Windows    | WSL2 recommended |

Zero external Python dependencies. The server runs on Python's standard library alone.

---

## Configuration

| Environment variable   | Default | Description                  |
|------------------------|---------|------------------------------|
| `ANTIGRAVITY_PORT`     | `4242`  | HTTP port for the skill server |

---

## Contributing

Pull requests are welcome. To add a new tool:

1. Add the function in `src/server.py`
2. Register it in `SKILL_MANIFEST["tools"]`
3. Add a route in `SkillHandler.do_POST`
4. Add a method in `src/client.js`
5. Write tests in `tests/`

---

## License

[MIT](LICENSE) © antigravity-claw contributors

---

<div align="center">

*"What goes up / need not come down / when you rewire the rules."*

⭐ Star this repo if it made you smile — or levitate.

</div>
