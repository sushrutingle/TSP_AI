"""
algorithm.py
------------
Core Hill Climbing Algorithm for the Travelling Salesman Problem (TSP).

Algorithm Description:
    Hill Climbing is a local search heuristic that iteratively improves
    a candidate solution by evaluating neighbouring solutions and moving
    to the best neighbour that reduces the objective function value.
    It continues until no improvement can be found (local optimum).

Pseudocode:
    ─────────────────────────────────────────────────────────────────
    FUNCTION HillClimbing(cities, dist_matrix, max_iter, restarts):

        best_global_route  ← None
        best_global_distance ← ∞

        FOR restart = 1 TO restarts:
            current_route    ← RandomPermutation(cities)
            current_distance ← TotalDistance(current_route)

            FOR iteration = 1 TO max_iter:
                improved ← FALSE

                FOR each pair (i, j) in route [2-opt swap]:
                    neighbour ← Swap(current_route, i, j)
                    neighbour_distance ← TotalDistance(neighbour)

                    IF neighbour_distance < current_distance:
                        current_route    ← neighbour
                        current_distance ← neighbour_distance
                        improved ← TRUE
                        BREAK   ← first-improvement strategy

                IF NOT improved:
                    BREAK           ← local optimum reached

            IF current_distance < best_global_distance:
                best_global_route    ← current_route
                best_global_distance ← current_distance

        RETURN best_global_route, best_global_distance
    ─────────────────────────────────────────────────────────────────

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

import random
import time
from itertools import combinations
from distances import build_distance_matrix, total_route_distance


class HillClimbingOptimizer:
    """
    Hill Climbing optimizer for the Travelling Salesman Problem.

    Supports:
    - Random-restart hill climbing (avoids single local-optima trap)
    - 2-opt neighbourhood generation (city swap)
    - First-improvement and best-improvement strategies
    - Convergence logging for analysis
    """

    def __init__(self, cities: list, max_iterations: int = 10000,
                 restarts: int = 5, strategy: str = "first"):
        """
        Parameters
        ----------
        cities         : list of str  — City names to include in the route
        max_iterations : int          — Maximum iterations per restart
        restarts       : int          — Number of random restarts
        strategy       : str          — 'first' or 'best' improvement
        """
        if len(cities) < 2:
            raise ValueError("At least 2 cities are required.")

        self.cities         = list(cities)
        self.max_iterations = max_iterations
        self.restarts       = restarts
        self.strategy       = strategy

        # Build pairwise distance matrix once
        self.dist_matrix    = build_distance_matrix(self.cities)

        # Results populated after run()
        self.best_route     = None
        self.best_distance  = float("inf")
        self.convergence    = []   # list of (iteration, distance) per restart
        self.all_restarts   = []   # detailed log per restart
        self.elapsed_time   = 0.0

    # ------------------------------------------------------------------ #
    #  Neighbour generation — 2-opt swap                                   #
    # ------------------------------------------------------------------ #

    def _generate_neighbour_swap(self, route: list, i: int, j: int) -> list:
        """Swap cities at positions i and j to generate a neighbour."""
        neighbour = route[:]
        neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
        return neighbour

    def _generate_neighbour_2opt(self, route: list, i: int, j: int) -> list:
        """Reverse the sub-segment between i and j (2-opt move)."""
        neighbour = route[:i] + list(reversed(route[i:j + 1])) + route[j + 1:]
        return neighbour

    # ------------------------------------------------------------------ #
    #  Single hill-climbing run from a given start                         #
    # ------------------------------------------------------------------ #

    def _run_single(self, initial_route: list):
        """
        Execute a single hill-climbing run from the given initial route.

        Returns
        -------
        (best_route, best_distance, history)
        """
        current_route    = initial_route[:]
        current_distance = total_route_distance(current_route, self.dist_matrix)
        history          = [(0, current_distance)]

        for iteration in range(1, self.max_iterations + 1):
            improved        = False
            best_neighbour  = None
            best_nd         = current_distance
            n               = len(current_route)

            for i in range(n - 1):
                for j in range(i + 1, n):
                    # Try both swap and 2-opt moves
                    for move_fn in [self._generate_neighbour_swap,
                                    self._generate_neighbour_2opt]:
                        neighbour = move_fn(current_route, i, j)
                        nd        = total_route_distance(neighbour, self.dist_matrix)

                        if nd < best_nd:
                            best_nd       = nd
                            best_neighbour = neighbour

                            if self.strategy == "first":
                                # First-improvement: move immediately
                                current_route    = best_neighbour
                                current_distance = best_nd
                                history.append((iteration, current_distance))
                                improved = True
                                break

                    if improved and self.strategy == "first":
                        break

                if improved and self.strategy == "first":
                    break

            # Best-improvement strategy: apply the best found after full scan
            if not improved and self.strategy == "best" and best_neighbour:
                current_route    = best_neighbour
                current_distance = best_nd
                history.append((iteration, current_distance))
                improved = True

            if not improved:
                # Local optimum — no better neighbour found
                break

        return current_route, current_distance, history

    # ------------------------------------------------------------------ #
    #  Public interface                                                     #
    # ------------------------------------------------------------------ #

    def run(self, progress_callback=None):
        """
        Execute the full Hill Climbing optimization with random restarts.

        Parameters
        ----------
        progress_callback : callable(restart_num, total_restarts)
                            Optional UI callback for progress updates.

        Returns
        -------
        (best_route : list, best_distance : float)
        """
        start_time = time.time()

        self.convergence   = []
        self.all_restarts  = []
        self.best_route    = None
        self.best_distance = float("inf")

        for restart in range(1, self.restarts + 1):
            if progress_callback:
                progress_callback(restart, self.restarts)

            # Generate a random initial route
            initial_route = self.cities[:]
            random.shuffle(initial_route)

            route, distance, history = self._run_single(initial_route)

            self.all_restarts.append({
                "restart":        restart,
                "initial_route":  initial_route,
                "final_route":    route,
                "final_distance": distance,
                "history":        history,
                "iterations":     len(history),
            })

            if distance < self.best_distance:
                self.best_distance = distance
                self.best_route    = route
                self.convergence   = history

        self.elapsed_time = round(time.time() - start_time, 4)
        return self.best_route, self.best_distance

    def get_summary(self) -> dict:
        """Return a structured summary of the optimization results."""
        if not self.best_route:
            return {}
        return {
            "best_route":        self.best_route,
            "best_distance_km":  self.best_distance,
            "num_cities":        len(self.cities),
            "restarts":          self.restarts,
            "strategy":          self.strategy,
            "elapsed_sec":       self.elapsed_time,
            "route_with_return": self.best_route + [self.best_route[0]],
        }

    def get_route_segments(self) -> list:
        """
        Return a list of (city_from, city_to, distance_km) tuples
        for the best route, useful for display tables.
        """
        if not self.best_route:
            return []
        segments = []
        route = self.best_route + [self.best_route[0]]
        for i in range(len(route) - 1):
            a, b = route[i], route[i + 1]
            segments.append((a, b, self.dist_matrix.get((a, b), 0.0)))
        return segments
