"""
map_visualizer.py
-----------------
Generates an interactive Folium map showing the optimized route
between selected Indian cities, exported as an HTML file.

Features:
- City markers with name labels and coordinate popups
- Route polyline in the optimized order (blue)
- Return leg highlighted (dashed orange)
- Fit-bounds to show all cities automatically
- HTML export for offline browser viewing

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

import os
import webbrowser
import folium
from folium.plugins import AntPath
from cities_data import get_coordinates


def generate_route_map(best_route: list,
                       best_distance: float,
                       output_path: str = "output/route_map.html",
                       open_browser: bool = True) -> str:
    """
    Generate an interactive Folium map for the optimized route.

    Parameters
    ----------
    best_route    : list of str  — Ordered city names (optimized route)
    best_distance : float        — Total route distance in km
    output_path   : str          — Where to save the HTML file
    open_browser  : bool         — Auto-open in default web browser

    Returns
    -------
    str — Absolute path to the saved HTML file
    """
    if not best_route:
        raise ValueError("Route is empty — cannot generate map.")

    # ── Gather coordinates ─────────────────────────────────────────── #
    coords = []
    for city in best_route:
        c = get_coordinates(city)
        if c:
            coords.append((city, c[0], c[1]))

    if not coords:
        raise ValueError("No valid coordinates found for the given cities.")

    # ── Compute map centre ─────────────────────────────────────────── #
    avg_lat = sum(c[1] for c in coords) / len(coords)
    avg_lon = sum(c[2] for c in coords) / len(coords)

    # ── Create Folium map ──────────────────────────────────────────── #
    fmap = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=5,
        tiles="OpenStreetMap",
        prefer_canvas=True,
    )

    # ── Add title box ──────────────────────────────────────────────── #
    title_html = f"""
    <div style="
        position: fixed;
        top: 10px; left: 50%; transform: translateX(-50%);
        z-index: 1000;
        background: rgba(13, 17, 46, 0.92);
        color: #ffffff;
        padding: 10px 24px;
        border-radius: 12px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(99,179,237,0.4);
    ">
        🗺️ Hill Climbing Route Optimizer &nbsp;|&nbsp;
        <span style="color:#63b3ed;">Total Distance: {best_distance:.1f} km</span>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(title_html))

    # ── City markers ───────────────────────────────────────────────── #
    colors = ["#4ade80", "#f59e0b", "#60a5fa", "#f87171",
              "#a78bfa", "#34d399", "#fb923c", "#e879f9"]

    for idx, (city, lat, lon) in enumerate(coords):
        color = colors[idx % len(colors)]
        order_label = f"#{idx + 1}"

        # Custom DivIcon for a styled numbered marker
        icon_html = f"""
        <div style="
            background:{color};
            color:#000;
            font-weight:bold;
            border-radius:50%;
            width:28px; height:28px;
            display:flex; align-items:center; justify-content:center;
            font-size:12px;
            border:2px solid #fff;
            box-shadow:0 2px 6px rgba(0,0,0,0.4);
        ">{idx + 1}</div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<b>{city}</b><br>Lat: {lat:.4f}°<br>Lon: {lon:.4f}°<br>Stop #{idx+1}",
                max_width=200
            ),
            tooltip=f"{order_label} {city}",
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(28, 28),
                icon_anchor=(14, 14),
            ),
        ).add_to(fmap)

        # City label
        folium.Marker(
            location=[lat + 0.25, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:11px;font-weight:600;color:#1a202c;'
                     f'background:rgba(255,255,255,0.85);padding:2px 5px;'
                     f'border-radius:4px;white-space:nowrap;">{city}</div>',
                icon_size=(120, 20),
                icon_anchor=(60, 0),
            ),
        ).add_to(fmap)

    # ── Route polyline (animated ant-path) ────────────────────────── #
    route_latlons = [(c[1], c[2]) for c in coords]

    # Main route — animated
    AntPath(
        locations=route_latlons,
        color="#3b82f6",
        weight=4,
        opacity=0.85,
        delay=600,
        dash_array=[10, 20],
        tooltip="Optimized Route",
    ).add_to(fmap)

    # Return leg — dashed orange
    if len(route_latlons) > 1:
        AntPath(
            locations=[route_latlons[-1], route_latlons[0]],
            color="#f59e0b",
            weight=3,
            opacity=0.75,
            delay=1000,
            dash_array=[5, 15],
            tooltip="Return to Start",
        ).add_to(fmap)

    # Also draw a light grey line underneath for clarity
    folium.PolyLine(
        locations=route_latlons + [route_latlons[0]],
        color="#94a3b8",
        weight=2,
        opacity=0.3,
    ).add_to(fmap)

    # ── Fit bounds to all markers ──────────────────────────────────── #
    fmap.fit_bounds(
        [[min(c[1] for c in coords) - 0.5, min(c[2] for c in coords) - 0.5],
         [max(c[1] for c in coords) + 0.5, max(c[2] for c in coords) + 0.5]]
    )

    # ── Distance legend ────────────────────────────────────────────── #
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 30px; right: 20px;
        z-index: 1000;
        background: rgba(13, 17, 46, 0.88);
        color: #e2e8f0;
        padding: 12px 18px;
        border-radius: 10px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        border: 1px solid rgba(99,179,237,0.3);
        min-width: 200px;
    ">
        <div style="font-weight:700;font-size:14px;margin-bottom:8px;color:#63b3ed;">
            📊 Route Summary
        </div>
        <div>🏙️ Cities: <b>{len(coords)}</b></div>
        <div>📏 Distance: <b>{best_distance:.1f} km</b></div>
        <div style="margin-top:8px;font-size:11px;color:#94a3b8;">
            — Optimized Route &nbsp; - - Return Leg
        </div>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend_html))

    # ── Save to file ───────────────────────────────────────────────── #
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    abs_path = os.path.abspath(output_path)
    fmap.save(abs_path)

    if open_browser:
        webbrowser.open(f"file:///{abs_path}")

    return abs_path
