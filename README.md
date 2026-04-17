# roboharness Showcase

Runnable, self-contained examples that prove roboharness works as a `pip install` dependency in your existing project.

Each showcase is an independent directory with its own virtualenv-friendly dependencies. No monorepo required.

## Quick Start

```bash
git clone https://github.com/roboharness/showcase.git
cd showcase/lerobot-eval
./run.sh
```

## Showcase Matrix

| Framework   | Status | Hardware | Runtime | Last Tested |
|-------------|--------|----------|---------|-------------|
| LeRobot     | ✅     | GPU      | ~5 min  | v0.2.2      |
| GR00T WBC   | ✅     | GPU      | ~3 min  | v0.2.2      |

## Install Modes

Each `run.sh` automatically creates a virtual environment and installs roboharness.

**Default** — latest from git main (so showcases always ship the newest integrations):
```bash
./run.sh
```

**PyPI** — stable release:
```bash
ROBOHARNESS_PYPI=1 ./run.sh
```

**Local source** — test your local roboharness changes:
```bash
ROBOHARNESS_SRC=../roboharness ./run.sh
```

## Smoke Mode

Quick validation without downloading large checkpoints:

```bash
SMOKE=1 ./run.sh
```

- **LeRobot smoke:** <60s, runs 1 episode of 10 steps on CartPole
- **GR00T WBC smoke:** <120s, validates imports and runs 1 dummy simulation step

## Design Principles

1. **roboharness is a pip dependency**, not a submodule or framework you live inside
2. **Each showcase is self-contained** — create a separate virtualenv per showcase
3. **Standard command contract** — every showcase runs with `./run.sh` and produces `results.json`
4. **Smoke mode** — every showcase supports `SMOKE=1 ./run.sh` for fast CI validation

## Adding a New Showcase

1. Create a new directory with `README.md`, `requirements.txt`, `run.sh`, and the showcase script
2. Implement smoke mode so CI stays fast
3. Add a row to the matrix above
4. Add a job to `.github/workflows/ci.yml`
