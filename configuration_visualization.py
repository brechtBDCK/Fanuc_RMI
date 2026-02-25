#!/usr/bin/env python3
"""
Visual FANUC configuration explorer (GUI).

Run:
    python3 configuration_visualization.py

Purpose:
- Toggle Front / Up / Left / Flip.
- Adjust Turn4 / Turn5 / Turn6.
- See a live visual posture sketch and wrist wrap indicators.
- Optionally load the latest Configuration from robot_position_cartesian.jsonl.
"""

from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk


# ---- quick defaults ----
DEFAULT_FRONT = 1
DEFAULT_UP = 1
DEFAULT_LEFT = 0
DEFAULT_FLIP = 0
DEFAULT_TURN4 = 0
DEFAULT_TURN5 = 0
DEFAULT_TURN6 = 0
DEFAULT_JSONL_PATH = "robot_position_cartesian.jsonl"


@dataclass
class FanucConfig:
    front: int = DEFAULT_FRONT
    up: int = DEFAULT_UP
    left: int = DEFAULT_LEFT
    flip: int = DEFAULT_FLIP
    turn4: int = DEFAULT_TURN4
    turn5: int = DEFAULT_TURN5
    turn6: int = DEFAULT_TURN6

    def clamp(self) -> "FanucConfig":
        self.front = 1 if int(self.front) else 0
        self.up = 1 if int(self.up) else 0
        self.left = 1 if int(self.left) else 0
        self.flip = 1 if int(self.flip) else 0
        self.turn4 = int(self.turn4)
        self.turn5 = int(self.turn5)
        self.turn6 = int(self.turn6)
        return self

    def as_rmi_configuration(self) -> dict:
        return {
            "Front": self.front,
            "Up": self.up,
            "Left": self.left,
            "Flip": self.flip,
            "Turn4": self.turn4,
            "Turn5": self.turn5,
            "Turn6": self.turn6,
        }


def _read_latest_config_from_jsonl(path: Path) -> FanucConfig | None:
    if not path.exists():
        return None
    for raw in reversed(path.read_text(encoding="utf-8").splitlines()):
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
        ).clamp()
    return None


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FANUC Configuration Visualizer")
        self.root.geometry("1180x700")
        self.root.minsize(1000, 620)

        self._syncing = False

        self.front_var = tk.IntVar(value=DEFAULT_FRONT)
        self.up_var = tk.IntVar(value=DEFAULT_UP)
        self.left_var = tk.IntVar(value=DEFAULT_LEFT)
        self.flip_var = tk.IntVar(value=DEFAULT_FLIP)
        self.turn4_var = tk.IntVar(value=DEFAULT_TURN4)
        self.turn5_var = tk.IntVar(value=DEFAULT_TURN5)
        self.turn6_var = tk.IntVar(value=DEFAULT_TURN6)
        self.path_var = tk.StringVar(value=DEFAULT_JSONL_PATH)
        self.status_var = tk.StringVar(value="Ready.")
        self.summary_var = tk.StringVar()
        self.config_json_var = tk.StringVar()

        self._build_ui()
        self._bind_updates()
        self.redraw()

    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        controls = ttk.Frame(self.root, padding=12)
        controls.grid(row=0, column=0, sticky="nsew")
        controls.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Configuration Controls", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        path_row = ttk.Frame(controls)
        path_row.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        path_row.columnconfigure(0, weight=1)
        ttk.Entry(path_row, textvariable=self.path_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(path_row, text="Load Latest", command=self.load_latest).grid(row=0, column=1, padx=(8, 0))

        bool_box = ttk.LabelFrame(controls, text="Branch Flags", padding=8)
        bool_box.grid(row=2, column=0, sticky="ew")
        ttk.Checkbutton(bool_box, text="Front", variable=self.front_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(bool_box, text="Up", variable=self.up_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(bool_box, text="Left", variable=self.left_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(bool_box, text="Flip", variable=self.flip_var).grid(row=3, column=0, sticky="w")

        turn_box = ttk.LabelFrame(controls, text="Wrist Turns", padding=8)
        turn_box.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self._add_spin(turn_box, "Turn4", self.turn4_var, 0)
        self._add_spin(turn_box, "Turn5", self.turn5_var, 1)
        self._add_spin(turn_box, "Turn6", self.turn6_var, 2)

        btn_row = ttk.Frame(controls)
        btn_row.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(btn_row, text="Reset Defaults", command=self.reset_defaults).grid(row=0, column=0, sticky="w")

        ttk.Label(controls, textvariable=self.summary_var, wraplength=320, justify="left").grid(
            row=5, column=0, sticky="ew", pady=(12, 0)
        )
        ttk.Label(controls, text="RMI Configuration JSON:", font=("TkDefaultFont", 9, "bold")).grid(
            row=6, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Label(
            controls,
            textvariable=self.config_json_var,
            wraplength=320,
            justify="left",
            foreground="#1f2937",
        ).grid(row=7, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(controls, textvariable=self.status_var, foreground="#334155").grid(
            row=8, column=0, sticky="w", pady=(12, 0)
        )

        self.canvas = tk.Canvas(self.root, bg="#f6f3eb", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

    def _add_spin(self, parent: ttk.LabelFrame, text: str, var: tk.IntVar, row: int):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w")
        ttk.Spinbox(parent, from_=-10, to=10, textvariable=var, width=6).grid(row=row, column=1, padx=(8, 0))

    def _bind_updates(self):
        vars_to_watch = [
            self.front_var,
            self.up_var,
            self.left_var,
            self.flip_var,
            self.turn4_var,
            self.turn5_var,
            self.turn6_var,
        ]
        for var in vars_to_watch:
            var.trace_add("write", lambda *_: self.redraw())
        self.canvas.bind("<Configure>", lambda _: self.redraw())

    @staticmethod
    def _safe_int(var: tk.IntVar, default: int = 0) -> int:
        try:
            return int(var.get())
        except (tk.TclError, ValueError):
            return default

    def current_config(self) -> FanucConfig:
        cfg = FanucConfig(
            front=1 if self._safe_int(self.front_var, DEFAULT_FRONT) else 0,
            up=1 if self._safe_int(self.up_var, DEFAULT_UP) else 0,
            left=1 if self._safe_int(self.left_var, DEFAULT_LEFT) else 0,
            flip=1 if self._safe_int(self.flip_var, DEFAULT_FLIP) else 0,
            turn4=self._safe_int(self.turn4_var, DEFAULT_TURN4),
            turn5=self._safe_int(self.turn5_var, DEFAULT_TURN5),
            turn6=self._safe_int(self.turn6_var, DEFAULT_TURN6),
        ).clamp()
        return cfg

    def _apply_config_to_ui(self, cfg: FanucConfig):
        self._syncing = True
        try:
            self.front_var.set(cfg.front)
            self.up_var.set(cfg.up)
            self.left_var.set(cfg.left)
            self.flip_var.set(cfg.flip)
            self.turn4_var.set(cfg.turn4)
            self.turn5_var.set(cfg.turn5)
            self.turn6_var.set(cfg.turn6)
        finally:
            self._syncing = False
        self.redraw()

    def reset_defaults(self):
        self._apply_config_to_ui(FanucConfig().clamp())
        self.status_var.set("Reset to defaults.")

    def load_latest(self):
        path = Path(self.path_var.get().strip() or DEFAULT_JSONL_PATH)
        cfg = _read_latest_config_from_jsonl(path)
        if cfg is None:
            self.status_var.set(f"No valid Configuration found in {path}")
            return
        self._apply_config_to_ui(cfg)
        self.status_var.set(f"Loaded latest Configuration from {path}")

    def redraw(self):
        if self._syncing:
            return
        cfg = self.current_config()
        self.config_json_var.set(json.dumps(cfg.as_rmi_configuration(), indent=2))
        self.summary_var.set(
            "Shoulder: {front}\nElbow: {up}\nArm side: {left}\nWrist style: {flip}\n"
            "Turn offsets: J4 {t4:+d}, J5 {t5:+d}, J6 {t6:+d}".format(
                front="front" if cfg.front else "back",
                up="up" if cfg.up else "down",
                left="lefty" if cfg.left else "righty",
                flip="flip" if cfg.flip else "non-flip",
                t4=cfg.turn4,
                t5=cfg.turn5,
                t6=cfg.turn6,
            )
        )
        self._draw_scene(cfg)

    def _draw_scene(self, cfg: FanucConfig):
        c = self.canvas
        c.delete("all")

        w = max(700, c.winfo_width())
        h = max(420, c.winfo_height())
        panel_w = min(390, max(320, int(w * 0.34)))
        panel_x1 = w - panel_w - 18
        panel_x2 = w - 18

        # Background grid
        for x in range(0, w, 40):
            c.create_line(x, 0, x, h, fill="#e2e8f0")
        for y in range(0, h, 40):
            c.create_line(0, y, w, y, fill="#e2e8f0")

        # Drawing area center (left side of help panel)
        draw_left = 140
        draw_right = max(draw_left + 420, panel_x1 - 24)
        cx = int((draw_left + draw_right) * 0.5)
        cy = int(h * 0.48)

        # Branch directions
        front_dir = 1 if cfg.front else -1
        up_dir = -1 if cfg.up else 1
        side_dir = -1 if cfg.left else 1
        flip_dir = 1 if cfg.flip else -1

        base = (cx, cy + 120)
        shoulder = (cx + side_dir * 70, cy + 30)
        elbow = (shoulder[0] + front_dir * 160, shoulder[1] + up_dir * 90)
        wrist = (elbow[0] + front_dir * 130, elbow[1] + up_dir * 45)
        tool = (wrist[0] + flip_dir * 60, wrist[1] - up_dir * 20)

        # Axes indicators
        c.create_line(40, 60, 130, 60, width=3, fill="#1d4ed8", arrow=tk.LAST)
        c.create_text(40, 44, text="Front axis (+)", fill="#1d4ed8", anchor="w")
        c.create_line(40, 90, 40, 150, width=3, fill="#9333ea", arrow=tk.LAST)
        c.create_text(48, 154, text="Down", fill="#9333ea", anchor="w")

        # Robot links
        c.create_line(*base, *shoulder, width=14, fill="#334155", capstyle=tk.ROUND)
        c.create_line(*shoulder, *elbow, width=12, fill="#0f766e", capstyle=tk.ROUND)
        c.create_line(*elbow, *wrist, width=10, fill="#b45309", capstyle=tk.ROUND)
        c.create_line(*wrist, *tool, width=8, fill="#dc2626", capstyle=tk.ROUND)

        # Joints
        for x, y, r, color in [
            (base[0], base[1], 11, "#0f172a"),
            (shoulder[0], shoulder[1], 10, "#1e293b"),
            (elbow[0], elbow[1], 9, "#1e293b"),
            (wrist[0], wrist[1], 8, "#1e293b"),
        ]:
            c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

        c.create_polygon(
            tool[0],
            tool[1],
            tool[0] - 16 * front_dir,
            tool[1] - 8,
            tool[0] - 16 * front_dir,
            tool[1] + 8,
            fill="#111827",
            outline="",
        )

        c.create_text(base[0], base[1] + 22, text="Base", fill="#0f172a")
        c.create_text(shoulder[0], shoulder[1] - 18, text="Shoulder", fill="#0f172a")
        c.create_text(elbow[0], elbow[1] - 18, text="Elbow", fill="#0f172a")
        c.create_text(wrist[0], wrist[1] - 18, text="Wrist", fill="#0f172a")

        # Turn gauges
        gx = int(w * 0.16)
        gy = int(h * 0.30)
        self._draw_turn_gauge(gx, gy, "Turn4", cfg.turn4)
        self._draw_turn_gauge(gx, gy + 150, "Turn5", cfg.turn5)
        self._draw_turn_gauge(gx, gy + 300, "Turn6", cfg.turn6)

        c.create_text(
            int((draw_left + draw_right) * 0.5),
            24,
            text="Live branch sketch (conceptual, not IK-accurate)",
            fill="#0f172a",
            font=("TkDefaultFont", 10, "bold"),
        )

        self._draw_help_panel(cfg, panel_x1, 20, panel_x2, h - 20)

    def _draw_turn_gauge(self, x: int, y: int, name: str, turns: int):
        c = self.canvas
        color = "#16a34a" if turns >= 0 else "#ea580c"
        c.create_text(x, y - 38, text=name, fill="#0f172a", font=("TkDefaultFont", 10, "bold"))
        c.create_oval(x - 20, y - 20, x + 20, y + 20, outline="#475569", width=2, fill="#f8fafc")

        loops = min(abs(turns), 8)
        for i in range(loops):
            pad = 24 + i * 5
            start = 15 if turns >= 0 else 200
            extent = 300 if turns >= 0 else -300
            c.create_arc(
                x - pad,
                y - pad,
                x + pad,
                y + pad,
                start=start,
                extent=extent,
                style=tk.ARC,
                width=2,
                outline=color,
            )
        c.create_text(x, y + 42, text=f"{turns:+d} ({turns * 360:+d} deg)", fill="#0f172a")
        if abs(turns) > 8:
            c.create_text(x, y + 58, text=f"... +{abs(turns) - 8} more wraps", fill="#64748b")

    def _draw_help_panel(self, cfg: FanucConfig, x1: int, y1: int, x2: int, y2: int):
        c = self.canvas
        c.create_rectangle(x1, y1, x2, y2, fill="#fffdfa", outline="#cbd5e1", width=2)

        title_x = x1 + 14
        c.create_text(
            title_x,
            y1 + 14,
            anchor="nw",
            text="What These Settings Mean (Noob Version)",
            fill="#0f172a",
            font=("TkDefaultFont", 10, "bold"),
        )

        state_text = (
            f"Current: Front={cfg.front}, Up={cfg.up}, Left={cfg.left}, Flip={cfg.flip}, "
            f"Turns=({cfg.turn4:+d}, {cfg.turn5:+d}, {cfg.turn6:+d})"
        )
        c.create_text(
            title_x,
            y1 + 38,
            anchor="nw",
            text=state_text,
            fill="#334155",
            font=("TkDefaultFont", 9),
            width=max(120, x2 - x1 - 28),
        )

        explainer = (
            "Front: Picks one shoulder branch for the same XYZWPR target.\n"
            "1 means front-side branch, 0 means the opposite branch.\n\n"
            "Up: Picks elbow-up vs elbow-down style posture.\n"
            "1 = elbow-up, 0 = elbow-down.\n\n"
            "Left: Picks lefty/righty arm side branch.\n"
            "1 = lefty style, 0 = righty style.\n\n"
            "Flip: Picks wrist flip branch.\n"
            "1 = flip wrist branch, 0 = non-flip branch.\n\n"
            "Turn4/5/6: Wrist wrap counts for J4/J5/J6.\n"
            "+1 means one extra full +360 deg turn, -1 means -360 deg.\n"
            "They keep orientation continuity and cable-friendly wrist posture.\n\n"
            "Important: Same Cartesian pose can map to multiple joint solutions.\n"
            "These fields tell FANUC which one to use. Wrong branch can cause\n"
            "\"position not reachable\" on linear moves."
        )
        c.create_text(
            title_x,
            y1 + 72,
            anchor="nw",
            text=explainer,
            fill="#1e293b",
            font=("TkDefaultFont", 9),
            width=max(120, x2 - x1 - 28),
        )


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
