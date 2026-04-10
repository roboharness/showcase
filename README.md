# RoboHarness Showcases

Runnable, self-contained examples for robotics hardware integrations.

Each showcase includes: hardware config, launch scripts, simulation setup, and CI.

## Available Showcases

| Showcase | Framework | Hardware | Status |
|----------|-----------|----------|--------|
| `gr00t/` | GR00T (1X) | H1 / H1-2 | 🔴 planned |
| `pi0/` | Pi0 (Physical Intelligence) |ANYBotics | 🔴 planned |
| `lerobot/` | LeRobot (HuggingFace) | low-cost arms | 🔴 planned |
| `sonic/` | SONIC (NVIDIA) | GR00T-K | 🔴 planned |
| `isaac-lab/` | Isaac Lab (NVIDIA) | any | 🔴 planned |

## Architecture

```
showcase/
├── README.md
├── requirements.txt
├── gr00t/          # GR00T integration example
├── pi0/            # Pi0 integration example  
├── lerobot/        # LeRobot integration example
├── sonic/          # SONIC integration example
└── isaac-lab/      # Isaac Lab integration example
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/roboharness/showcase.git
cd showcase

# Install dependencies
pip install -r requirements.txt

# Run a specific showcase
cd gr00t && ./run.sh
```

## CI Status

| Showcase | Linux | ROS2 | Simulation |
|----------|-------|------|------------|
| gr00t | ❌ | ❌ | ❌ |
| pi0 | ❌ | ❌ | ❌ |
| lerobot | ❌ | ❌ | ❌ |
| sonic | ❌ | ❌ | ❌ |
| isaac-lab | ❌ | ❌ | ❌ |

*CI badges will be added as showccases are implemented.*
