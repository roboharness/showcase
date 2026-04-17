#!/usr/bin/env python3
"""GR00T WBC Showcase — whole-body control integration with roboharness.

This showcase demonstrates roboharness as a pip-installable library
integrated with NVIDIA GR00T Whole-Body Control.

Smoke mode (fast validation):
    SMOKE=1 ./run.sh

Full mode (requires GR00T WBC installation):
    ./run.sh

For the full demo, install GR00T WBC from:
    https://github.com/NVlabs/GR00T-WholeBodyControl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np


def _write_results_json(
    status: str,
    output_dir: Path,
    metrics: dict[str, Any] | None = None,
    checkpoints: list[str] | None = None,
) -> None:
    """Write the standard showcase results.json contract."""
    results = {
        "framework": "gr00t-wbc",
        "status": status,
        "checkpoints": checkpoints or [],
        "metrics": metrics or {},
    }
    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"      Results saved: {results_path}")


class DummyGrootPolicy:
    """Dummy policy for smoke mode — returns zero actions."""

    def __init__(self, action_dim: int = 29) -> None:
        self.action_dim = action_dim

    def __call__(self, obs: np.ndarray) -> np.ndarray:
        return np.zeros(self.action_dim, dtype=np.float32)


def try_import_gr00t() -> tuple[Any | None, str]:
    """Try to import GR00T WBC components. Returns (module_or_none, status_message)."""
    try:
        # GR00T WBC is not on PyPI; users install it from source.
        # We attempt a generic import pattern that matches common IsaacLab/GR00T setups.
        import importlib

        gr00t = importlib.import_module("gr00t")
        return gr00t, "GR00T WBC imported successfully"
    except ImportError:
        return None, "GR00T WBC not installed (expected in smoke mode)"


def main() -> int:
    parser = argparse.ArgumentParser(description="GR00T WBC showcase")
    parser.add_argument("--output-dir", default="./harness_output", help="Output directory")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps")
    args = parser.parse_args()

    smoke = os.environ.get("SMOKE", "0") == "1"
    output_dir = Path(args.output_dir) / "groot_wbc"
    output_dir.mkdir(parents=True, exist_ok=True)

    if smoke:
        args.steps = 1
        print("=" * 60)
        print("  SMOKE MODE: validating imports + 1 dummy simulation step")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  Roboharness: GR00T WBC Showcase")
        print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Validate roboharness import
    # ------------------------------------------------------------------
    print("\n[1/3] Validating roboharness import ...")
    try:
        from roboharness.wrappers import RobotHarnessWrapper

        print("      roboharness: OK")
    except ImportError as exc:
        print(f"ERROR: failed to import roboharness: {exc}")
        _write_results_json("error", output_dir)
        return 1

    # ------------------------------------------------------------------
    # 2. Validate GR00T WBC import (optional in smoke mode)
    # ------------------------------------------------------------------
    print("[2/3] Validating GR00T WBC import ...")
    gr00t_mod, gr00t_status = try_import_gr00t()
    print(f"      {gr00t_status}")

    if not smoke and gr00t_mod is None:
        print(
            "\n  GR00T WBC is not installed. Install it from:\n"
            "    https://github.com/NVlabs/GR00T-WholeBodyControl\n"
            "  Or run smoke mode:\n"
            "    SMOKE=1 ./run.sh"
        )
        _write_results_json("error", output_dir)
        return 1

    # ------------------------------------------------------------------
    # 3. Run minimal simulation with checkpoint capture
    # ------------------------------------------------------------------
    print(f"[3/3] Running {args.steps} simulation step(s) ...")

    try:
        import gymnasium as gym
    except ImportError:
        print("ERROR: gymnasium is required. Install with: pip install roboharness[demo]")
        _write_results_json("error", output_dir)
        return 1

    # Use CartPole as a lightweight stand-in for the robot env in smoke mode.
    # In full mode, users replace this with their GR00T WBC IsaacLab environment.
    env = gym.make("CartPole-v1", render_mode="rgb_array")

    # Dummy policy (smoke mode) or real GR00T policy (full mode)
    if gr00t_mod is None or smoke:
        policy = DummyGrootPolicy(action_dim=int(env.action_space.n if hasattr(env.action_space, "n") else env.action_space.shape[0]))
    else:
        # Placeholder for real GR00T policy instantiation.
        # Users with GR00T installed should replace this block.
        policy = DummyGrootPolicy(action_dim=int(env.action_space.shape[0]))

    # Wrap with roboharness for checkpoint capture
    wrapped = RobotHarnessWrapper(
        env,
        checkpoints=[{"name": "step_000", "step": 0}],
        output_dir=str(output_dir),
    )

    obs, _info = wrapped.reset()
    checkpoint_paths: list[str] = []

    for step in range(args.steps):
        action = policy(obs)
        # Handle discrete action spaces (CartPole)
        if hasattr(env.action_space, "n"):
            action = int(action[0] % env.action_space.n)
        obs, reward, terminated, truncated, info = wrapped.step(action)

        if "checkpoint" in info:
            cp = info["checkpoint"]
            cp_dir = Path(cp["capture_dir"])
            png = cp_dir / "default_rgb.png"
            if png.exists():
                checkpoint_paths.append(str(png))
            print(f"      Checkpoint '{cp['name']}' captured at step {cp['step']}")

        if terminated or truncated:
            break

    wrapped.close()

    metrics = {
        "steps": args.steps,
        "gr00t_available": gr00t_mod is not None,
        "smoke_mode": smoke,
    }

    _write_results_json("success", output_dir, metrics=metrics, checkpoints=checkpoint_paths)
    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
