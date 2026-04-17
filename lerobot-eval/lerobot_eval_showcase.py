#!/usr/bin/env python3
"""LeRobot Evaluation Showcase — visual regression testing for robot policies.

This showcase demonstrates roboharness as a pip-installable library.
It uses the public ``roboharness.evaluate.lerobot_plugin`` API to evaluate
policies with visual checkpoints and structured JSON output.

Smoke mode (fast, no checkpoint downloads):
    SMOKE=1 ./run.sh

Full mode (real LeRobot checkpoint):
    ./run.sh --checkpoint-path /path/to/checkpoint --repo-id lerobot/unitree-g1-mujoco
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

from roboharness.evaluate.lerobot_plugin import (
    LeRobotEvalConfig,
    check_eval_threshold,
    evaluate_lerobot_policy,
    evaluate_policy,
)


def _random_policy(obs: np.ndarray, action_space: Any = None) -> np.ndarray:
    """Fallback random policy when no trained policy is available."""
    if action_space is not None and hasattr(action_space, "sample"):
        return action_space.sample()
    return np.zeros(2, dtype=np.float32)


def _write_results_json(
    report: Any,
    output_dir: Path,
    status: str,
) -> None:
    """Write the standard showcase results.json contract."""
    # Collect checkpoint screenshot paths from all episodes
    checkpoints: list[str] = []
    for ep in report.episodes:
        for cp_dir in ep.checkpoint_dirs:
            png_path = Path(cp_dir) / "default_rgb.png"
            if png_path.exists():
                checkpoints.append(str(png_path))

    results = {
        "framework": "lerobot",
        "status": status,
        "checkpoints": checkpoints,
        "metrics": {
            "mean_reward": report.mean_reward,
            "success_rate": report.success_rate,
            "mean_episode_length": report.mean_episode_length,
            "n_episodes": report.n_episodes,
            "wall_time": report.wall_time,
        },
    }

    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"      Results saved: {results_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="LeRobot evaluation showcase")
    parser.add_argument(
        "--env",
        default="CartPole-v1",
        help="Gymnasium environment ID (default: CartPole-v1)",
    )
    parser.add_argument("--n-episodes", type=int, default=10, help="Number of episodes")
    parser.add_argument("--max-steps", type=int, default=500, help="Max steps per episode")
    parser.add_argument("--output-dir", default="./harness_output", help="Output directory")
    parser.add_argument(
        "--checkpoint-steps",
        type=int,
        nargs="*",
        default=[10, 50],
        help="Steps at which to capture checkpoints",
    )
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=0.0,
        help="Minimum success rate threshold",
    )
    parser.add_argument(
        "--min-mean-reward",
        type=float,
        default=None,
        help="Minimum mean reward threshold",
    )
    parser.add_argument(
        "--assert-threshold",
        action="store_true",
        help="Exit non-zero if thresholds are not met",
    )
    parser.add_argument(
        "--checkpoint-path",
        type=str,
        default=None,
        help="Path to a LeRobot policy checkpoint directory",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default=None,
        help="HuggingFace repo ID for the LeRobot environment",
    )
    args = parser.parse_args()

    smoke = os.environ.get("SMOKE", "0") == "1"
    if smoke:
        args.n_episodes = 1
        args.max_steps = 10
        args.checkpoint_steps = [5]
        args.checkpoint_path = None
        print("=" * 60)
        print("  SMOKE MODE: 1 episode, 10 steps, CartPole fallback")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  Roboharness: LeRobot Evaluation Showcase")
        print("=" * 60)

    output_dir = Path(args.output_dir) / "lerobot_eval"

    config = LeRobotEvalConfig(
        n_episodes=args.n_episodes,
        max_steps_per_episode=args.max_steps,
        checkpoint_steps=args.checkpoint_steps or [],
        output_dir=str(output_dir),
    )

    # Create environment / load policy
    if args.checkpoint_path:
        print(f"\n[1/3] Loading LeRobot policy from: {args.checkpoint_path}")
        if not Path(args.checkpoint_path).exists():
            print(f"ERROR: Checkpoint path does not exist: {args.checkpoint_path}")
            return 1

        print(f"[2/3] Evaluating ({args.n_episodes} episodes, max {args.max_steps} steps each) ...")
        report = evaluate_lerobot_policy(
            checkpoint_path=args.checkpoint_path,
            repo_id=args.repo_id,
            config=config,
        )
    else:
        print(f"\n[1/3] Creating environment: {args.env}")
        try:
            import gymnasium as gym

            env = gym.make(args.env, render_mode="rgb_array")
        except ImportError:
            print("ERROR: gymnasium is required. Install with: pip install roboharness[demo]")
            return 1

        print(f"      Obs space: {env.observation_space}")
        print(f"      Act space: {env.action_space}")

        action_space = env.action_space

        def policy_fn(obs: np.ndarray) -> np.ndarray:
            return _random_policy(obs, action_space)

        print(f"[2/3] Evaluating ({args.n_episodes} episodes, max {args.max_steps} steps each) ...")
        report = evaluate_policy(env, policy_fn, config)
        env.close()

    # Report results
    print("[3/3] Results:")
    print(f"      Episodes:        {report.n_episodes}")
    print(f"      Success rate:    {report.success_rate:.1%}")
    print(f"      Mean reward:     {report.mean_reward:.2f}")
    print(f"      Mean ep length:  {report.mean_episode_length:.1f}")
    print(f"      Wall time:       {report.wall_time:.2f}s")

    if not args.checkpoint_path and not smoke:
        print(
            "\n  Tip: pass --checkpoint-path to evaluate a real LeRobot policy:\n"
            "    ./run.sh --checkpoint-path /path/to/checkpoint --repo-id lerobot/unitree-g1-mujoco"
        )

    # CI gate
    status = "success"
    if args.assert_threshold:
        passed = check_eval_threshold(
            report,
            min_success_rate=args.min_success_rate,
            min_mean_reward=args.min_mean_reward,
        )
        print(f"\n  Threshold check: {'PASSED' if passed else 'FAILED'}")
        if not passed:
            status = "error"
            if args.assert_threshold:
                _write_results_json(report, output_dir, status)
                return 1

    _write_results_json(report, output_dir, status)
    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
