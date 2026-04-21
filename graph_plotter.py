"""
graph_plotter.py
----------------
Matplotlib-based route graph visualizer.

Shows:
- Cities as nodes plotted on a 2D coordinate plane (lon, lat)
- Edges representing the optimized route order
- A bar chart of segment distances
- A convergence plot (distance vs. iteration)

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

import matplotlib
matplotlib.use("TkAgg")  # Ensure Tkinter-compatible backend

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from cities_data import get_coordinates

# ── Style configuration ──────────────────────────────────────── #
DARK_BG     = "#0f172a"
CARD_BG     = "#1e293b"
ACCENT_BLUE = "#3b82f6"
ACCENT_GRN  = "#22c55e"
ACCENT_ORG  = "#f59e0b"
TEXT_COLOR  = "#e2e8f0"
GRID_COLOR  = "#334155"


def _apply_dark_style(ax, title: str = "", xlabel: str = "", ylabel: str = ""):
    """Apply consistent dark theme styling to an axes object."""
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.5, alpha=0.6)
    if title:   ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    if xlabel:  ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:  ax.set_ylabel(ylabel, fontsize=9)


def plot_route(best_route: list,
               best_distance: float,
               segments: list,
               convergence: list = None):
    """
    Create a multi-panel route visualization figure.

    Parameters
    ----------
    best_route    : list      — Ordered city names
    best_distance : float     — Total kilometres
    segments      : list      — [(from, to, km), ...] segment list
    convergence   : list      — [(iteration, distance), ...] history

    Returns
    -------
    matplotlib.figure.Figure
    """
    n_cols = 2 if convergence else 2
    n_rows = 2
    fig = plt.figure(figsize=(15, 10), facecolor=DARK_BG)
    fig.suptitle(
        "AI-Based Route Optimization — Hill Climbing Algorithm",
        color=TEXT_COLOR, fontsize=14, fontweight="bold", y=0.98
    )

    # ── Panel 1: Route map ───────────────────────────────────────── #
    ax_map = fig.add_subplot(2, 2, (1, 3))
    _apply_dark_style(ax_map, "Optimized Route Map (Indian Cities)", "Longitude (°E)", "Latitude (°N)")

    lats, lons, names = [], [], []
    for city in best_route:
        c = get_coordinates(city)
        if c:
            lats.append(c[0])
            lons.append(c[1])
            names.append(city)

    # Draw route edges
    route_lons = lons + [lons[0]]
    route_lats = lats + [lats[0]]

    ax_map.plot(route_lons[:-1], route_lats[:-1],
                color=ACCENT_BLUE, linewidth=2, zorder=2, alpha=0.8, label="Route")
    ax_map.plot([route_lons[-2], route_lons[-1]],
                [route_lats[-2], route_lats[-1]],
                color=ACCENT_ORG, linewidth=2, linestyle="--",
                zorder=2, alpha=0.8, label="Return Leg")

    # Draw arrows along route segments
    for i in range(len(lons)):
        j = (i + 1) % len(lons)
        ax_map.annotate(
            "", xy=(lons[j], lats[j]), xytext=(lons[i], lats[i]),
            arrowprops=dict(arrowstyle="->", color=ACCENT_BLUE, lw=1.5),
            zorder=3
        )

    # Draw city nodes
    ax_map.scatter(lons, lats, s=120, color=ACCENT_GRN,
                   zorder=5, edgecolors="white", linewidths=1.5)
    ax_map.scatter(lons[0], lats[0], s=200, color=ACCENT_ORG,
                   zorder=6, edgecolors="white", linewidths=2,
                   marker="*", label="Start / End")

    # City labels
    for i, name in enumerate(names):
        ax_map.annotate(
            f" {i+1}. {name}",
            xy=(lons[i], lats[i]),
            fontsize=8, color=TEXT_COLOR,
            fontweight="bold",
            xytext=(4, 4), textcoords="offset points"
        )

    total_dist_text = f"Total Distance: {best_distance:.1f} km  |  Cities: {len(best_route)}"
    ax_map.text(0.02, 0.02, total_dist_text, transform=ax_map.transAxes,
                fontsize=9, color=ACCENT_ORG, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", alpha=0.85))

    ax_map.legend(facecolor=CARD_BG, labelcolor=TEXT_COLOR, fontsize=8,
                  framealpha=0.8, loc="upper right")

    # ── Panel 2: Segment distances bar chart ─────────────────────── #
    ax_bar = fig.add_subplot(2, 2, 2)
    _apply_dark_style(ax_bar, "Segment Distances (km)", "Route Segment", "Distance (km)")

    if segments:
        seg_labels = [f"{s[0][:3]}→{s[1][:3]}" for s in segments]
        seg_dists  = [s[2] for s in segments]
        bar_colors = [ACCENT_BLUE if d < np.mean(seg_dists) else ACCENT_ORG for d in seg_dists]

        bars = ax_bar.bar(range(len(seg_labels)), seg_dists,
                          color=bar_colors, edgecolor=DARK_BG, linewidth=0.5)
        ax_bar.set_xticks(range(len(seg_labels)))
        ax_bar.set_xticklabels(seg_labels, rotation=45, ha="right", fontsize=7)

        for bar, val in zip(bars, seg_dists):
            ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                        f"{val:.0f}", ha="center", va="bottom",
                        fontsize=7, color=TEXT_COLOR)

    # ── Panel 3: Convergence plot ─────────────────────────────────── #
    ax_conv = fig.add_subplot(2, 2, 4)
    _apply_dark_style(ax_conv, "Algorithm Convergence", "Iteration", "Total Distance (km)")

    if convergence and len(convergence) > 1:
        iters  = [c[0] for c in convergence]
        dists  = [c[1] for c in convergence]
        ax_conv.plot(iters, dists, color=ACCENT_GRN, linewidth=2, zorder=3)
        ax_conv.fill_between(iters, dists, alpha=0.15, color=ACCENT_GRN)
        ax_conv.scatter(iters[0], dists[0], color=ACCENT_ORG, s=80, zorder=5, label="Start")
        ax_conv.scatter(iters[-1], dists[-1], color=ACCENT_BLUE, s=80, zorder=5, label="Optimum")
        ax_conv.legend(facecolor=CARD_BG, labelcolor=TEXT_COLOR, fontsize=8)
    else:
        ax_conv.text(0.5, 0.5, "Single-step solution\n(already optimal)",
                     ha="center", va="center", color=TEXT_COLOR, fontsize=10,
                     transform=ax_conv.transAxes)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def show_route_plot(best_route, best_distance, segments, convergence=None):
    """Display the route visualization in a Matplotlib window."""
    fig = plot_route(best_route, best_distance, segments, convergence)
    plt.show()
    return fig


def save_route_plot(best_route, best_distance, segments, convergence=None,
                    filepath: str = "output/route_graph.png", dpi: int = 150):
    """Save the route visualization to a PNG file."""
    import os
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    fig = plot_route(best_route, best_distance, segments, convergence)
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    return os.path.abspath(filepath)
