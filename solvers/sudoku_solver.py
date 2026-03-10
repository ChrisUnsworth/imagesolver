"""
Sudoku solver using Google OR-Tools MIP.

Formulation
-----------
Binary decision variables:
    x[i, j, d] = 1  iff cell (i, j) contains digit d   (i, j, d all 0-indexed)

Constraints:
    1. Each cell holds exactly one digit.
    2. Each digit appears exactly once in every row.
    3. Each digit appears exactly once in every column.
    4. Each digit appears exactly once in every 3x3 box.
    5. Pre-filled clues are fixed to 1.

Objective: feasibility only (no cost term needed).
"""

from ortools.linear_solver import pywraplp


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """
    Solve a sudoku puzzle using a MIP formulation.

    Parameters
    ----------
    grid : 9×9 list of ints, 0 = empty, 1-9 = given clue.

    Returns
    -------
    9×9 list of ints with the solution, or None if infeasible.
    """
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        solver = pywraplp.Solver.CreateSolver("CBC_MIXED_INTEGER_PROGRAMMING")
    if solver is None:
        raise RuntimeError("No MIP solver backend available in OR-Tools.")

    solver.SuppressOutput()

    # ── Variables ─────────────────────────────────────────────────────────────
    x = {}
    for i in range(9):
        for j in range(9):
            for d in range(9):
                x[i, j, d] = solver.BoolVar(f"x[{i},{j},{d}]")

    # ── Constraints ───────────────────────────────────────────────────────────

    # 1. Each cell has exactly one digit.
    for i in range(9):
        for j in range(9):
            solver.Add(solver.Sum([x[i, j, d] for d in range(9)]) == 1)

    # 2. Each digit appears exactly once per row.
    for i in range(9):
        for d in range(9):
            solver.Add(solver.Sum([x[i, j, d] for j in range(9)]) == 1)

    # 3. Each digit appears exactly once per column.
    for j in range(9):
        for d in range(9):
            solver.Add(solver.Sum([x[i, j, d] for i in range(9)]) == 1)

    # 4. Each digit appears exactly once per 3x3 box.
    for bi in range(3):
        for bj in range(3):
            for d in range(9):
                solver.Add(
                    solver.Sum([
                        x[bi * 3 + di, bj * 3 + dj, d]
                        for di in range(3)
                        for dj in range(3)
                    ]) == 1
                )

    # 5. Fix pre-filled clues.
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                d = grid[i][j] - 1
                solver.Add(x[i, j, d] == 1)

    # ── Solve ─────────────────────────────────────────────────────────────────
    solver.set_time_limit(30_000)  # 30 s safety limit
    status = solver.Solve()

    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return None

    # ── Extract solution ───────────────────────────────────────────────────────
    solution = []
    for i in range(9):
        row = []
        for j in range(9):
            for d in range(9):
                if x[i, j, d].solution_value() > 0.5:
                    row.append(d + 1)
                    break
        solution.append(row)

    return solution
