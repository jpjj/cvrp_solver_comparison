from typing import Callable
from cvrp_solver_comparison.domain.models import Instance, Solution
from cvrp_solver_comparison.solver.ortools import solve_with_ortools
from cvrp_solver_comparison.solver.pyhygese import solve_with_pyhygese
from cvrp_solver_comparison.solver.pyvrp import solve_with_pyvrp
from cvrp_solver_comparison.solver.rustvrp.rustvrp import solve_with_rustvrp
from cvrp_solver_comparison.solver.timefold import solve_with_timefold
from cvrp_solver_comparison.solver.vroom import solve_with_vroom


# Type alias for solver functions
SolverFn = Callable[[Instance, int], Solution]


def create_solver(method: str, *, time_limit: int = 60) -> SolverFn:
    """
    Factory function that returns a configured solver function.

    Args:
        method: One of 'pyvrp', 'ortools', 'vroom', 'timefold', 'rustvrp', 'pyhygese'
        time_limit: Maximum solve time in seconds


    Returns:
        A function that takes a Instance and returns a Solution
    """

    solvers: dict[str, SolverFn] = {
        "pyvrp": solve_with_pyvrp,
        "ortools": solve_with_ortools,
        "vroom": solve_with_vroom,
        "timefold": solve_with_timefold,
        "rustvrp": solve_with_rustvrp,
        "pyhygese": solve_with_pyhygese,
    }

    if method not in solvers:
        available = ", ".join(solvers.keys())
        raise ValueError(f"Unknown method '{method}'. Available: {available}")

    return solvers[method]
