# LeRobot Evaluation Showcase

Visual regression testing for LeRobot policies using roboharness.

## Environment Requirements

- **Python:** 3.10+
- **CUDA:** 11.8+ (for GPU inference)
- **GPU:** Not strictly required; CPU works for small policies
- **Expected runtime:** ~5 minutes for 10 episodes
- **Disk space:** ~2 GB for LeRobot + MuJoCo dependencies

> **Warning:** Create a separate virtualenv for each showcase to avoid dependency conflicts.

## Quick Start

```bash
# From PyPI (default)
./run.sh

# From local roboharness source
ROBOHARNESS_SRC=../roboharness ./run.sh
```

## Smoke Mode

Fast validation without downloading real checkpoints:

```bash
SMOKE=1 ./run.sh
```

Runs 1 episode of 10 steps on CartPole-v1 with a random policy. Target: <60 seconds.

## Full Demo

Evaluate a real LeRobot policy checkpoint:

```bash
./run.sh \
  --checkpoint-path /path/to/lerobot/checkpoint \
  --repo-id lerobot/unitree-g1-mujoco
```

## Output

```
./harness_output/lerobot_eval/
├── episode_000/
│   └── step_0005/
│       └── default_rgb.png
├── episode_001/
│   └── ...
└── results.json
```

`results.json` follows the standard showcase contract:

```json
{
  "framework": "lerobot",
  "status": "success",
  "checkpoints": ["harness_output/lerobot_eval/episode_000/step_0005/default_rgb.png"],
  "metrics": {
    "mean_reward": 0.0,
    "success_rate": 0.0,
    "mean_episode_length": 10.0,
    "n_episodes": 1,
    "wall_time": 1.23
  }
}
```
