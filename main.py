"""
main.py
-------
Entry point for the AI-Based Route Optimization application.
Launches the Tkinter GUI for the Hill Climbing TSP Optimizer.

Application Features:
  • Select 2–10 Indian cities from styled dropdown menus
  • Configure algorithm parameters (restarts, strategy)
  • Run the Hill Climbing optimization
  • View results: optimized route, total distance, segment table
  • Visualize: Matplotlib route graph + Folium interactive map

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys

# ── Internal modules ────────────────────────────────────────────── #
from cities_data  import get_city_list
from algorithm    import HillClimbingOptimizer
from graph_plotter import show_route_plot
from map_visualizer import generate_route_map

# ── Theme Constants ──────────────────────────────────────────────── #
BG_DARK      = "#0f172a"
BG_CARD      = "#1e293b"
BG_CARD2     = "#243044"
ACCENT_BLUE  = "#3b82f6"
ACCENT_GRN   = "#22c55e"
ACCENT_ORG   = "#f59e0b"
ACCENT_PRP   = "#a78bfa"
TEXT_PRIM    = "#f1f5f9"
TEXT_SEC     = "#94a3b8"
BORDER       = "#334155"
BTN_HOVER    = "#2563eb"
DANGER       = "#ef4444"

FONT_TITLE   = ("Segoe UI", 18, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_BODY    = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
FONT_LABEL   = ("Segoe UI", 9, "bold")

MAX_CITIES   = 10
MIN_CITIES   = 2


# ════════════════════════════════════════════════════════════════════ #
#  Custom Styled Widgets                                               #
# ════════════════════════════════════════════════════════════════════ #

def styled_frame(parent, bg=BG_CARD, bd=0, relief="flat", **kw):
    f = tk.Frame(parent, bg=bg, bd=bd, relief=relief, **kw)
    return f

def label(parent, text, font=FONT_BODY, color=TEXT_PRIM, bg=BG_CARD, anchor="w", **kw):
    return tk.Label(parent, text=text, font=font, fg=color, bg=bg, anchor=anchor, **kw)

def separator(parent, bg=BORDER):
    return tk.Frame(parent, bg=bg, height=1)


# ════════════════════════════════════════════════════════════════════ #
#  City Selector Row Widget                                            #
# ════════════════════════════════════════════════════════════════════ #

class CitySelectorRow:
    """A styled row with a label + combobox for selecting one Indian city."""

    def __init__(self, parent, idx: int, cities: list, bg=BG_CARD2):
        self.frame = tk.Frame(parent, bg=bg)
        self.frame.pack(fill="x", padx=12, pady=3)

        tk.Label(
            self.frame, text=f"  City {idx:02d}",
            font=FONT_LABEL, fg=ACCENT_BLUE, bg=bg, width=8, anchor="w"
        ).pack(side="left")

        self.var = tk.StringVar()
        style_name = f"City{idx}.TCombobox"

        cb = ttk.Combobox(
            self.frame,
            textvariable=self.var,
            values=["-- Select --"] + cities,
            state="readonly",
            width=24,
            font=FONT_BODY,
        )
        cb.set("-- Select --")
        cb.pack(side="left", padx=6)
        self.combobox = cb

    def get(self) -> str:
        v = self.var.get()
        return v if v != "-- Select --" else ""

    def set(self, value: str):
        self.var.set(value)


# ════════════════════════════════════════════════════════════════════ #
#  Main Application Window                                             #
# ════════════════════════════════════════════════════════════════════ #

class RouteOptimizerApp:
    """
    Main Tkinter application for Hill Climbing Route Optimization.

    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │  Title Banner                                           │
    ├────────────────┬────────────────────────────────────────┤
    │  Left Panel    │  Right Panel                           │
    │  ─ City Inputs │  ─ Results Display                     │
    │  ─ Parameters  │  ─ Route Table                         │
    │  ─ Run Button  │  ─ Log Area                            │
    └────────────────┴────────────────────────────────────────┘
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()
        self._configure_ttk_styles()
        self._build_ui()

        self.optimizer   = None
        self.last_result = None

    # ── Window Setup ─────────────────────────────────────────────── #

    def _configure_root(self):
        self.root.title("AI Route Optimizer — Hill Climbing Algorithm")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        # Centre on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 1100) // 2
        y = (self.root.winfo_screenheight() - 750)  // 2
        self.root.geometry(f"1100x750+{x}+{y}")

    def _configure_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=BG_CARD2,
            background=BG_CARD2,
            foreground=TEXT_PRIM,
            selectbackground=ACCENT_BLUE,
            selectforeground=TEXT_PRIM,
            bordercolor=BORDER,
            arrowcolor=ACCENT_BLUE,
            lightcolor=BG_CARD,
            darkcolor=BG_CARD,
        )
        style.map("TCombobox", fieldbackground=[("readonly", BG_CARD2)])

        style.configure(
            "Treeview",
            background=BG_CARD,
            foreground=TEXT_PRIM,
            rowheight=26,
            fieldbackground=BG_CARD,
            bordercolor=BORDER,
            font=FONT_BODY,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_CARD2,
            foreground=ACCENT_BLUE,
            font=FONT_LABEL,
            relief="flat",
        )
        style.map("Treeview", background=[("selected", ACCENT_BLUE)])

        style.configure(
            "TScale",
            background=BG_CARD,
            troughcolor=BORDER,
            slidercolor=ACCENT_BLUE,
        )

        style.configure(
            "TProgressbar",
            background=ACCENT_GRN,
            troughcolor=BORDER,
        )

    # ── UI Construction ───────────────────────────────────────────── #

    def _build_ui(self):
        self._build_title_bar()
        self._build_main_body()
        self._build_status_bar()

    def _build_title_bar(self):
        """Top banner with application title and subtitle."""
        banner = tk.Frame(self.root, bg=BG_CARD, height=75)
        banner.pack(fill="x", side="top")
        banner.pack_propagate(False)

        # Left: icon + title
        inner = tk.Frame(banner, bg=BG_CARD)
        inner.pack(side="left", padx=20, pady=10)

        tk.Label(inner, text="🗺", font=("Segoe UI Emoji", 26),
                 bg=BG_CARD, fg=ACCENT_BLUE).pack(side="left")
        text_box = tk.Frame(inner, bg=BG_CARD)
        text_box.pack(side="left", padx=10)
        tk.Label(text_box, text="AI Route Optimizer",
                 font=FONT_TITLE, fg=TEXT_PRIM, bg=BG_CARD).pack(anchor="w")
        tk.Label(text_box,
                 text="Hill Climbing Algorithm  •  Indian Cities  •  TSP",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

        # Right: version badge
        badge = tk.Frame(banner, bg=ACCENT_BLUE, padx=10, pady=4)
        badge.pack(side="right", padx=20, pady=22)
        tk.Label(badge, text="v1.0  AI Project",
                 font=FONT_LABEL, fg="white", bg=ACCENT_BLUE).pack()

        separator(self.root, bg=ACCENT_BLUE).pack(fill="x")

    def _build_main_body(self):
        """Two-column main area: left (input) + right (output)."""
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        self._build_left_panel(body)
        self._build_right_panel(body)

    def _build_left_panel(self, parent):
        """City selection + algorithm parameters + run button."""
        left = tk.Frame(parent, bg=BG_DARK, width=340)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)

        # ── City Selection Card ─────────────────────────────────── #
        city_card = tk.Frame(left, bg=BG_CARD, bd=0)
        city_card.pack(fill="x", pady=(0, 6))

        hdr = tk.Frame(city_card, bg=BG_CARD)
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(hdr, text="🏙  Select Cities", font=FONT_HEADING,
                 fg=ACCENT_BLUE, bg=BG_CARD).pack(side="left")
        self._num_cities_var = tk.IntVar(value=5)
        tk.Label(hdr, text="Count:", font=FONT_BODY, fg=TEXT_SEC, bg=BG_CARD).pack(side="right", padx=(0,4))
        spin = tk.Spinbox(
            hdr, from_=MIN_CITIES, to=MAX_CITIES,
            textvariable=self._num_cities_var,
            width=3, font=FONT_BODY,
            bg=BG_CARD2, fg=TEXT_PRIM, relief="flat",
            buttonbackground=BG_CARD2,
            command=self._rebuild_city_rows,
        )
        spin.pack(side="right")

        separator(city_card).pack(fill="x", padx=12, pady=(0, 6))

        # Scrollable city selector area
        scroll_frame = tk.Frame(city_card, bg=BG_CARD)
        scroll_frame.pack(fill="x", padx=4, pady=(0, 8))
        self._city_rows_frame = scroll_frame

        self._city_rows: list[CitySelectorRow] = []
        all_cities = get_city_list()
        self._all_cities = all_cities
        self._rebuild_city_rows()

        # Quick-fill buttons
        btn_row = tk.Frame(city_card, bg=BG_CARD)
        btn_row.pack(fill="x", padx=12, pady=(0, 10))
        self._make_btn(btn_row, "⚡ Sample Set", self._fill_sample, ACCENT_PRP, font=FONT_BODY).pack(side="left", padx=(0,4))
        self._make_btn(btn_row, "🔄 Clear All",  self._clear_cities, BORDER, font=FONT_BODY).pack(side="left")

        # ── Algorithm Parameters Card ───────────────────────────── #
        param_card = tk.Frame(left, bg=BG_CARD)
        param_card.pack(fill="x", pady=(0, 6))

        tk.Label(param_card, text="⚙  Algorithm Parameters",
                 font=FONT_HEADING, fg=ACCENT_BLUE, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,6))
        separator(param_card).pack(fill="x", padx=12, pady=(0,8))

        self._restarts_var  = tk.IntVar(value=8)
        self._max_iter_var  = tk.IntVar(value=5000)
        self._strategy_var  = tk.StringVar(value="first")

        self._param_row(param_card, "Random Restarts:", self._restarts_var,
                        from_=1, to=20, tooltip="More restarts = better chance of global optimum")
        self._param_row(param_card, "Max Iterations:",  self._max_iter_var,
                        from_=500, to=50000, tooltip="Per restart iteration limit")

        strat_f = tk.Frame(param_card, bg=BG_CARD)
        strat_f.pack(fill="x", padx=12, pady=(4, 10))
        tk.Label(strat_f, text="Strategy:", font=FONT_BODY,
                 fg=TEXT_SEC, bg=BG_CARD, width=16, anchor="w").pack(side="left")
        for val, txt in [("first", "First-Improvement"), ("best", "Best-Improvement")]:
            tk.Radiobutton(
                strat_f, text=txt, variable=self._strategy_var, value=val,
                bg=BG_CARD, fg=TEXT_PRIM, selectcolor=ACCENT_BLUE,
                activebackground=BG_CARD, activeforeground=TEXT_PRIM,
                font=FONT_BODY, relief="flat",
            ).pack(side="left", padx=4)

        # ── Progress Bar ────────────────────────────────────────── #
        prog_f = tk.Frame(left, bg=BG_DARK)
        prog_f.pack(fill="x", pady=(0, 6))
        self._progress = ttk.Progressbar(prog_f, mode="determinate", style="TProgressbar")
        self._progress.pack(fill="x")
        self._prog_label = tk.Label(prog_f, text="", font=FONT_BODY, fg=TEXT_SEC, bg=BG_DARK)
        self._prog_label.pack(anchor="w")

        # ── Run Button ───────────────────────────────────────────── #
        run_btn = tk.Button(
            left,
            text="▶  Run Optimization",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_BLUE, fg="white",
            activebackground=BTN_HOVER, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            pady=12,
            command=self._run_optimization,
        )
        run_btn.pack(fill="x", pady=(0, 6))
        self._run_btn = run_btn

        # ── Map & Graph Buttons ──────────────────────────────────── #
        viz_row = tk.Frame(left, bg=BG_DARK)
        viz_row.pack(fill="x")
        self._map_btn = self._make_btn(viz_row, "🗺  Open Map",   self._open_map,   ACCENT_GRN)
        self._map_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self._graph_btn = self._make_btn(viz_row, "📊  Show Graph", self._show_graph, ACCENT_ORG)
        self._graph_btn.pack(side="left", fill="x", expand=True)
        self._map_btn.configure(state="disabled")
        self._graph_btn.configure(state="disabled")

    def _build_right_panel(self, parent):
        """Results display: summary cards, route table, log."""
        right = tk.Frame(parent, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        # ── Summary KPI Cards ────────────────────────────────────── #
        kpi_row = tk.Frame(right, bg=BG_DARK)
        kpi_row.pack(fill="x", pady=(0, 6))

        self._kpi_distance  = self._kpi_card(kpi_row, "Total Distance", "—",     "📏", ACCENT_BLUE)
        self._kpi_cities    = self._kpi_card(kpi_row, "Cities",          "—",     "🏙", ACCENT_GRN)
        self._kpi_time      = self._kpi_card(kpi_row, "Time (sec)",       "—",     "⏱", ACCENT_ORG)
        self._kpi_restarts  = self._kpi_card(kpi_row, "Restarts",         "—",     "🔄", ACCENT_PRP)

        # ── Route Table ──────────────────────────────────────────── #
        table_card = tk.Frame(right, bg=BG_CARD)
        table_card.pack(fill="both", expand=True, pady=(0, 6))

        tk.Label(table_card, text="📋  Optimized Route — Segment Details",
                 font=FONT_HEADING, fg=ACCENT_BLUE, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,6))
        separator(table_card).pack(fill="x", padx=12, pady=(0,6))

        tree_frame = tk.Frame(table_card, bg=BG_CARD)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        cols = ("#", "From", "To", "Distance (km)", "Cumulative (km)")
        self._tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            height=10, style="Treeview"
        )
        for col in cols:
            self._tree.heading(col, text=col)
            w = 40 if col == "#" else 130 if "Distance" in col or "Cumul" in col else 150
            self._tree.column(col, width=w, anchor="center" if col == "#" else "w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ── Log Area ─────────────────────────────────────────────── #
        log_card = tk.Frame(right, bg=BG_CARD, height=160)
        log_card.pack(fill="x")
        log_card.pack_propagate(False)

        hdr2 = tk.Frame(log_card, bg=BG_CARD)
        hdr2.pack(fill="x", padx=12, pady=(8, 4))
        tk.Label(hdr2, text="📝  Algorithm Log", font=FONT_HEADING,
                 fg=ACCENT_BLUE, bg=BG_CARD).pack(side="left")
        self._make_btn(hdr2, "Clear", self._clear_log, BORDER, font=("Segoe UI", 8)).pack(side="right")

        separator(log_card).pack(fill="x", padx=12, pady=(0, 4))
        self._log = scrolledtext.ScrolledText(
            log_card, height=6, font=FONT_MONO,
            bg="#0b1120", fg=ACCENT_GRN,
            insertbackground=TEXT_PRIM,
            relief="flat", bd=0, wrap="word",
        )
        self._log.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self._log_write("[SYSTEM] Route Optimizer initialized. Select cities and press Run.\n")

    def _build_status_bar(self):
        """Bottom status bar."""
        sb = tk.Frame(self.root, bg=BG_CARD, height=24)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        separator(sb, bg=BORDER).pack(fill="x")
        self._status_var = tk.StringVar(value="Ready — Select cities to begin optimization")
        tk.Label(sb, textvariable=self._status_var,
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=BG_CARD, anchor="w").pack(side="left", padx=12)
        tk.Label(sb, text="Final Year AI Project  |  Hill Climbing Route Optimizer",
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=BG_CARD).pack(side="right", padx=12)

    # ── Helper Builders ───────────────────────────────────────────── #

    def _make_btn(self, parent, text, command, color, font=FONT_LABEL, **kw):
        btn = tk.Button(
            parent, text=text, command=command,
            font=font, bg=color, fg="white",
            activebackground=color, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            padx=10, pady=6, **kw
        )
        return btn

    def _param_row(self, parent, label_text, variable, from_, to, tooltip=None):
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(fill="x", padx=12, pady=3)
        tk.Label(f, text=label_text, font=FONT_BODY, fg=TEXT_SEC,
                 bg=BG_CARD, width=18, anchor="w").pack(side="left")
        tk.Spinbox(
            f, from_=from_, to=to, textvariable=variable,
            width=8, font=FONT_BODY, bg=BG_CARD2, fg=TEXT_PRIM,
            relief="flat", buttonbackground=BG_CARD2,
        ).pack(side="left", padx=4)
        if tooltip:
            tk.Label(f, text=f"ℹ {tooltip[:35]}", font=("Segoe UI", 7),
                     fg=TEXT_SEC, bg=BG_CARD).pack(side="left", padx=4)

    def _kpi_card(self, parent, title, value, icon, color):
        card = tk.Frame(parent, bg=BG_CARD, padx=14, pady=10)
        card.pack(side="left", fill="x", expand=True, padx=3)
        tk.Label(card, text=icon, font=("Segoe UI Emoji", 18),
                 bg=BG_CARD, fg=color).pack(anchor="w")
        val_lbl = tk.Label(card, text=value, font=("Segoe UI", 16, "bold"),
                           bg=BG_CARD, fg=TEXT_PRIM)
        val_lbl.pack(anchor="w")
        tk.Label(card, text=title, font=FONT_BODY, bg=BG_CARD, fg=TEXT_SEC).pack(anchor="w")
        return val_lbl

    def _rebuild_city_rows(self):
        """Rebuild city selector rows based on current count."""
        for row in self._city_rows:
            row.frame.destroy()
        self._city_rows.clear()
        n = self._num_cities_var.get()
        for i in range(1, n + 1):
            row = CitySelectorRow(self._city_rows_frame, i, self._all_cities)
            self._city_rows.append(row)

    # ── Quick-fill ────────────────────────────────────────────────── #

    SAMPLE_CITIES = ["Delhi", "Jaipur", "Mumbai", "Pune", "Hyderabad",
                     "Bengaluru", "Chennai", "Kolkata", "Bhopal", "Lucknow"]

    def _fill_sample(self):
        n = self._num_cities_var.get()
        sample = self.SAMPLE_CITIES[:n]
        for i, row in enumerate(self._city_rows):
            if i < len(sample):
                row.set(sample[i])

    def _clear_cities(self):
        for row in self._city_rows:
            row.set("-- Select --")

    # ── Logging & Status ──────────────────────────────────────────── #

    def _log_write(self, text: str, tag=None):
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    # ── Optimization Logic ────────────────────────────────────────── #

    def _get_selected_cities(self):
        cities = []
        for row in self._city_rows:
            v = row.get()
            if v and v not in cities:
                cities.append(v)
        return cities

    def _run_optimization(self):
        cities = self._get_selected_cities()

        if len(cities) < MIN_CITIES:
            messagebox.showwarning("Insufficient Cities",
                                   f"Please select at least {MIN_CITIES} different cities.")
            return

        self._run_btn.configure(state="disabled", text="⏳  Optimizing...")
        self._map_btn.configure(state="disabled")
        self._graph_btn.configure(state="disabled")
        self._progress["value"] = 0
        self._set_status(f"Running Hill Climbing on {len(cities)} cities...")
        self._log_write(f"\n[RUN] Cities: {' → '.join(cities)}\n")
        self._log_write(f"[RUN] Restarts={self._restarts_var.get()}  "
                        f"MaxIter={self._max_iter_var.get()}  "
                        f"Strategy={self._strategy_var.get()}\n")

        thread = threading.Thread(target=self._optimize_thread, args=(cities,), daemon=True)
        thread.start()

    def _progress_cb(self, restart: int, total: int):
        pct = int((restart / total) * 100)
        self._progress["value"] = pct
        self._prog_label.configure(text=f"Restart {restart}/{total}")
        self._log_write(f"[RESTART {restart}/{total}] Running...\n")

    def _optimize_thread(self, cities: list):
        try:
            opt = HillClimbingOptimizer(
                cities=cities,
                max_iterations=self._max_iter_var.get(),
                restarts=self._restarts_var.get(),
                strategy=self._strategy_var.get(),
            )
            route, dist = opt.run(progress_callback=self._progress_cb)
            self.optimizer = opt
            self.last_result = (route, dist)
            self.root.after(0, self._on_result, route, dist, opt)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_result(self, route: list, dist: float, opt: HillClimbingOptimizer):
        summary  = opt.get_summary()
        segments = opt.get_route_segments()

        # ── Update KPI cards ─────────────────────────────────────── #
        self._kpi_distance.configure(text=f"{dist:.1f} km")
        self._kpi_cities.configure(text=str(len(route)))
        self._kpi_time.configure(text=f"{opt.elapsed_time:.3f}s")
        self._kpi_restarts.configure(text=str(self._restarts_var.get()))

        # ── Update route table ───────────────────────────────────── #
        for row in self._tree.get_children():
            self._tree.delete(row)

        cumulative = 0.0
        tags = ["even", "odd"]
        for i, (frm, to, km) in enumerate(segments):
            cumulative += km
            self._tree.insert("", "end",
                               values=(i + 1, frm, to, f"{km:.1f}", f"{cumulative:.1f}"),
                               tags=(tags[i % 2],))

        self._tree.tag_configure("even", background=BG_CARD)
        self._tree.tag_configure("odd",  background=BG_CARD2)

        # ── Log result ───────────────────────────────────────────── #
        route_str = " → ".join(route) + f" → {route[0]}"
        self._log_write(f"\n[✓] OPTIMIZED ROUTE:\n    {route_str}\n")
        self._log_write(f"[✓] Total Distance : {dist:.2f} km\n")
        self._log_write(f"[✓] Elapsed Time   : {opt.elapsed_time:.4f} s\n")
        self._log_write(f"[✓] Convergence    : {len(opt.convergence)} steps\n\n")

        # ── Reset UI ──────────────────────────────────────────────── #
        self._progress["value"] = 100
        self._prog_label.configure(text="Optimization complete ✓")
        self._run_btn.configure(state="normal", text="▶  Run Optimization")
        self._map_btn.configure(state="normal")
        self._graph_btn.configure(state="normal")
        self._set_status(f"✓ Optimization complete — {dist:.1f} km over {len(route)} cities")

    def _on_error(self, msg: str):
        self._run_btn.configure(state="normal", text="▶  Run Optimization")
        self._log_write(f"\n[ERROR] {msg}\n")
        self._set_status(f"Error: {msg}")
        messagebox.showerror("Optimization Error", msg)

    # ── Visualization Actions ─────────────────────────────────────── #

    def _open_map(self):
        if not self.last_result:
            messagebox.showinfo("No Results", "Run optimization first.")
            return
        route, dist = self.last_result
        try:
            path = generate_route_map(route, dist,
                                       output_path="output/route_map.html",
                                       open_browser=True)
            self._log_write(f"[MAP] Saved and opened: {path}\n")
            self._set_status(f"Map saved: {path}")
        except Exception as e:
            messagebox.showerror("Map Error", str(e))

    def _show_graph(self):
        if not self.last_result or not self.optimizer:
            messagebox.showinfo("No Results", "Run optimization first.")
            return
        route, dist = self.last_result
        segments    = self.optimizer.get_route_segments()
        convergence = self.optimizer.convergence
        try:
            show_route_plot(route, dist, segments, convergence)
        except Exception as e:
            messagebox.showerror("Graph Error", str(e))


# ════════════════════════════════════════════════════════════════════ #
#  Entry Point                                                         #
# ════════════════════════════════════════════════════════════════════ #

def main():
    root = tk.Tk()
    app  = RouteOptimizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
