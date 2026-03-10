"""
LinkedIn Queens solver using Google OR-Tools CP-SAT.

Rules
-----
Given an N×N grid divided into N coloured regions, place exactly N queens such that:
  1. Exactly one queen per row.
  2. Exactly one queen per column.
  3. Exactly one queen per coloured region.
  4. No two queens may be adjacent — including diagonally.

Model
-----
Binary decision variables:
    queen[i][j] = 1  iff a queen is placed at row i, column j.

Constraints mirror the four rules above.
"""

from ortools.sat.python import cp_model


def solve_queens(grid: list[list[int]]) -> list[list[int]] | None:
    """
    Solve a LinkedIn Queens puzzle.

    Parameters
    ----------
    grid : N×N list of ints where each value is a region ID (1 … N).

    Returns
    -------
    N×N list of ints where 1 = queen placed, 0 = empty.
    Returns None if the puzzle is infeasible or the solver times out.
    """
    n = len(grid)

    # Group cell coordinates by region ID.
    regions: dict[int, list[tuple[int, int]]] = {}
    for i in range(n):
        for j in range(n):
            regions.setdefault(grid[i][j], []).append((i, j))

    model = cp_model.CpModel()

    # ── Variables ──────────────────────────────────────────────────────────────
    queens = [[model.new_bool_var(f"q_{i}_{j}") for j in range(n)] for i in range(n)]

    # ── Constraints ────────────────────────────────────────────────────────────

    # 1. Exactly one queen per row.
    for i in range(n):
        model.add_exactly_one(queens[i])

    # 2. Exactly one queen per column.
    for j in range(n):
        model.add_exactly_one([queens[i][j] for i in range(n)])

    # 3. Exactly one queen per region.
    for region_cells in regions.values():
        model.add_exactly_one([queens[i][j] for i, j in region_cells])

    # 4. No two queens may be adjacent (including diagonally).
    for i in range(n):
        for j in range(n):
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n and (i, j) < (ni, nj):
                        model.add(queens[i][j] + queens[ni][nj] <= 1)

    # ── Solve ──────────────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    # ── Extract solution ───────────────────────────────────────────────────────
    return [
        [int(solver.value(queens[i][j])) for j in range(n)]
        for i in range(n)
    ]
