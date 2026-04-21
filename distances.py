"""
distances.py
------------
Module for computing geographical distances between Indian cities
using the Haversine formula, and building pairwise distance matrices.

Mathematical Model:
    Haversine Formula:
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        c = 2 × atan2(√a, √(1−a))
        d = R × c   where R = 6371 km (Earth radius)

Objective Function for TSP:
    Minimize f(R) = Σ d(cᵢ, cᵢ₊₁)  for i = 0 to n−1
    Subject to: each city visited exactly once; route returns to start.

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

import math
import numpy as np
from cities_data import get_coordinates

# Earth's mean radius in kilometres
EARTH_RADIUS_KM = 6371.0


def haversine_distance(city1: str, city2: str) -> float:
    """
    Compute the great-circle distance (km) between two cities
    using the Haversine formula.

    Parameters
    ----------
    city1 : str  — Name of the first city
    city2 : str  — Name of the second city

    Returns
    -------
    float — Distance in kilometres (0.0 if either city is not found)
    """
    coord1 = get_coordinates(city1)
    coord2 = get_coordinates(city2)

    if coord1 is None or coord2 is None:
        return 0.0

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(EARTH_RADIUS_KM * c, 2)


def haversine_coords(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute Haversine distance directly from coordinate pairs (degrees).

    Parameters
    ----------
    lat1, lon1 : float — Latitude, Longitude of point 1
    lat2, lon2 : float — Latitude, Longitude of point 2

    Returns
    -------
    float — Distance in kilometres
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(EARTH_RADIUS_KM * c, 2)


def build_distance_matrix(cities: list) -> dict:
    """
    Build a pairwise distance matrix for a list of cities.

    Parameters
    ----------
    cities : list of str — City names in order

    Returns
    -------
    dict — {(city_a, city_b): distance_km, ...}
    """
    matrix = {}
    n = len(cities)
    for i in range(n):
        for j in range(n):
            if i != j:
                key = (cities[i], cities[j])
                if key not in matrix:
                    dist = haversine_distance(cities[i], cities[j])
                    matrix[(cities[i], cities[j])] = dist
                    matrix[(cities[j], cities[i])] = dist
            else:
                matrix[(cities[i], cities[j])] = 0.0
    return matrix


def total_route_distance(route: list, dist_matrix: dict) -> float:
    """
    Compute the total distance of a route (including return to start).

    The objective function: f(R) = Σ d(cᵢ, cᵢ₊₁) + d(cₙ, c₀)

    Parameters
    ----------
    route      : list of str  — Ordered list of city names
    dist_matrix: dict         — Precomputed distance matrix

    Returns
    -------
    float — Total distance in kilometres
    """
    total = 0.0
    n = len(route)
    for i in range(n):
        city_a = route[i]
        city_b = route[(i + 1) % n]   # wraps around to start
        total += dist_matrix.get((city_a, city_b), 0.0)
    return round(total, 2)


def print_distance_matrix(cities: list, matrix: dict):
    """Pretty-print the distance matrix for debugging / display."""
    header = f"{'City':<20}" + "".join(f"{c:<18}" for c in cities)
    print(header)
    print("-" * len(header))
    for city_a in cities:
        row = f"{city_a:<20}"
        for city_b in cities:
            row += f"{matrix.get((city_a, city_b), 0):<18.1f}"
        print(row)
