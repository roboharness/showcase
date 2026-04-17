# GR00T WBC Showcase

Whole-body control integration with NVIDIA GR00T WBC and roboharness.

## Environment Requirements

- **Python:** 3.10+
- **CUDA:** 11.8+ (for GPU inference)
- **GPU:** Required for full IsaacLab simulation
- **Expected runtime:** ~3 minutes for a short trajectory
- **Disk space:** ~5 GB for IsaacLab + GR00T WBC dependencies

> **Warning:** Create a separate virtualenv for each showcase to avoid dependency conflicts.

## Quick Start

```bash
# Default: install roboharness from git main (latest)
SMOKE=1 ./run.sh

# From PyPI (stable release)
ROBOHARNESS_PYPI=1 SMOKE=1 ./run.sh

# From local roboharness source
ROBOHARNESS_SRC=../roboharness SMOKE=1 ./run.sh
```

## Full Demo

For the full demo, install GR00T WBC from source first:

```bash
# Install GR00T WBC (not on PyPI)
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd GR00T-WholeBodyControl
pip install -e .

# Then run the showcase
cd ../roboharness-showcase/groot-wbc
./run.sh
```

## Smoke Mode

Fast validation without loading real checkpoint weights:

```bash
SMOKE=1 ./run.sh
```

- Validates `roboharness` import
- Validates `gr00t` import (optional — OK if missing in smoke)
- Instantiates a dummy policy
- Runs 1 simulation step on CartPole-v1
- Captures a checkpoint screenshot
- Produces `results.json`

Target: <120 seconds.

## Output

```
./harness_output/groot_wbc/
├── step_000/
│   └── default_rgb.png
└── results.json
```

`results.json` follows the standard showcase contract:

```json
{
  "framework": "gr00t-wbc",
  "status": "success",
  "checkpoints": ["harness_output/groot_wbc/step_000/default_rgb.png"],
  "metrics": {
    "steps": 1,
    "gr00t_available": false,
    "smoke_mode": true
  }
}
```
