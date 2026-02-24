#!/usr/bin/env python3
"""
Quick prototype visualizer for FANUC RMI configuration fields:
Front, Up, Left, Flip, Turn4, Turn5, Turn6.

How to use:
1) Run: python3 configuration_visualization.py
2) Optionally type `load` to pull latest Configuration from robot_position_cartesian.jsonl
3) Toggle values and immediately see what branch you are selecting.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


# ---- Edit defaults here if you want a fixed starting point ----
DEFAULT_FRONT = 1
DEFAULT_UP = 1
DEFAULT_LEFT = 0
DEFAULT_FLIP = 0
DEFAULT_TURN4 = 0
DEFAULT_TURN5 = 0
DEFAULT_TURN6 = 0
DEFAULT_JSONL_PATH = Path("robot_position_cartesian.jsonl")


@dataclass
class FanucConfig:
    front: int = DEFAULT_FRONT
    up: int = DEFAULT_UP
    left: int = DEFAULT_LEFT
    flip: int = DEFAULT_FLIP
    turn4: int = DEFAULT_TURN4
    turn5: int = DEFAULT_TURN5
    turn6: int = DEFAULT_TURN6

    def clamp(self):
        self.front = 1 if int(self.front) else 0
        self.up = 1 if int(self.up) else 0
        self.left = 1 if int(self.left) else 0
        self.flip = 1 if int(self.flip) else 0
        self.turn4 = int(self.turn4)
        self.turn5 = int(self.turn5)
        self.turn6 = int(self.turn6)


def _read_latest_config_from_jsonl(path: Path) -> FanucConfig | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    for raw in reversed(lines):
        raw = raw.strip()
        if not raw or not raw.startswith("{"):
            continue
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError:
            continue
        cfg = packet.get("Configuration")
        if not isinstance(cfg, dict):
            continue
        return FanucConfig(
            front=int(cfg.get("Front", DEFAULT_FRONT)),
            up=int(cfg.get("Up", DEFAULT_UP)),
            left=int(cfg.get("Left", DEFAULT_LEFT)),
            flip=int(cfg.get("Flip", DEFAULT_FLIP)),
            turn4=int(cfg.get("Turn4", DEFAULT_TURN4)),
            turn5=int(cfg.get("Turn5", DEFAULT_TURN5)),
            turn6=int(cfg.get("Turn6", DEFAULT_TURN6)),
        )
    return None


def _flag_text(name: str, value: int) -> str:
    state = "1" if value else "0"
    meanings = {
        "Front": ("Front branch", "Back branch"),
        "Up": ("Elbow-up branch", "Elbow-down branch"),
        "Left": ("Lefty branch", "Righty branch"),
        "Flip": ("Wrist flip branch", "Wrist non-flip branch"),
    }
    on_txt, off_txt = meanings[name]
    return f"{name:<6} = {state}  -> {on_txt if value else off_txt}"


def _turn_text(joint_name: str, turns: int) -> str:
    deg = turns * 360
    sign = "+" if deg >= 0 else ""
    return f"{joint_name:<6} = {turns:+d}  -> wrist wrap offset {sign}{deg} deg"


def _print_visual(cfg: FanucConfig):
    cfg.clamp()
    print("\n" + "=" * 72)
    print("FANUC Configuration Visualizer")
    print("=" * 72)
    print(_flag_text("Front", cfg.front))
    print(_flag_text("Up", cfg.up))
    print(_flag_text("Left", cfg.left))
    print(_flag_text("Flip", cfg.flip))
    print("-" * 72)
    print(_turn_text("Turn4", cfg.turn4))
    print(_turn_text("Turn5", cfg.turn5))
    print(_turn_text("Turn6", cfg.turn6))
    print("-" * 72)
    print("Interpretation:")
    print(f"- Shoulder side: {'front' if cfg.front else 'back'}")
    print(f"- Elbow style:   {'up' if cfg.up else 'down'}")
    print(f"- Arm side:      {'lefty' if cfg.left else 'righty'}")
    print(f"- Wrist style:   {'flip' if cfg.flip else 'non-flip'}")
    print("- Turns choose J4/J5/J6 wrap counts (multiple 360 deg branches).")
    print("- Same Cartesian pose can have multiple valid branches.")
    print("- Use this to reason about branch selection; it is not an IK solver.")
    print("=" * 72)


def _print_help():
    print("\nCommands:")
    print("  f/u/l/p     toggle Front/Up/Left/Flip")
    print("  4/5/6       set Turn4/Turn5/Turn6 (integer)")
    print("  set a b c d e f g")
    print("              set Front Up Left Flip Turn4 Turn5 Turn6")
    print("              example: set 1 1 0 0 0 0 0")
    print("  load        load latest Configuration from robot_position_cartesian.jsonl")
    print("  show        reprint visualization")
    print("  help        show this help")
    print("  q           quit")


def main():
    cfg = FanucConfig()
    cfg.clamp()
    _print_visual(cfg)
    _print_help()

    while True:
        cmd = input("\nconfig> ").strip().lower()
        if not cmd:
            continue
        if cmd in {"q", "quit", "exit"}:
            break
        if cmd in {"help", "h", "?"}:
            _print_help()
            continue
        if cmd == "show":
            _print_visual(cfg)
            continue
        if cmd == "f":
            cfg.front = 0 if cfg.front else 1
            _print_visual(cfg)
            continue
        if cmd == "u":
            cfg.up = 0 if cfg.up else 1
            _print_visual(cfg)
            continue
        if cmd == "l":
            cfg.left = 0 if cfg.left else 1
            _print_visual(cfg)
            continue
        if cmd in {"p", "flip"}:
            cfg.flip = 0 if cfg.flip else 1
            _print_visual(cfg)
            continue
        if cmd == "4":
            cfg.turn4 = int(input("Turn4 integer: ").strip())
            _print_visual(cfg)
            continue
        if cmd == "5":
            cfg.turn5 = int(input("Turn5 integer: ").strip())
            _print_visual(cfg)
            continue
        if cmd == "6":
            cfg.turn6 = int(input("Turn6 integer: ").strip())
            _print_visual(cfg)
            continue
        if cmd.startswith("set "):
            parts = cmd.split()
            if len(parts) != 8:
                print("Expected: set Front Up Left Flip Turn4 Turn5 Turn6")
                continue
            try:
                cfg.front = int(parts[1])
                cfg.up = int(parts[2])
                cfg.left = int(parts[3])
                cfg.flip = int(parts[4])
                cfg.turn4 = int(parts[5])
                cfg.turn5 = int(parts[6])
                cfg.turn6 = int(parts[7])
                cfg.clamp()
                _print_visual(cfg)
            except ValueError:
                print("Invalid values. Use integers only.")
            continue
        if cmd == "load":
            loaded = _read_latest_config_from_jsonl(DEFAULT_JSONL_PATH)
            if loaded is None:
                print(f"No valid Configuration found in {DEFAULT_JSONL_PATH}")
            else:
                cfg = loaded
                cfg.clamp()
                print(f"Loaded from {DEFAULT_JSONL_PATH}")
                _print_visual(cfg)
            continue

        print("Unknown command. Type `help`.")


if __name__ == "__main__":
    main()
