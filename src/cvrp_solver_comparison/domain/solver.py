from typing import Callable
from pyvrp.stop import MaxRuntime

import pyvrp

from cvrp_solver_comparison.domain.models import Instance, Solution


# Type alias for solver functions
SolverFn = Callable[[Instance], Solution]


def create_solver(
    method: str, *, time_limit: float = 60.0, seed: int | None = None, **kwargs
) -> SolverFn:
    """
    Factory function that returns a configured solver function.

    Args:
        method: One of 'pyvrp', 'ortools', 'vroom', 'timefold', 'rustvrp', 'pyhygese'
        time_limit: Maximum solve time in seconds
        seed: Random seed for reproducibility
        **kwargs: Method-specific parameters

    Returns:
        A function that takes a Instance and returns a Solution
    """

    def solve_with_pyvrp(instance: Instance) -> Solution:
        # PyVRP implementation would go here
        # 1 transform instance object for pyvrp inputs
        m = pyvrp.Model()
        m.add_vehicle_type(
            num_available=len(instance.demand), capacity=instance.capacity
        )
        depot_coords = instance.node_coord[instance.depot[0]]
        m.add_depot(x=depot_coords[0], y=depot_coords[1])
        _ = [
            m.add_client(float(coord[0]), float(coord[1]), delivery=int(demand))
            for coord, demand in list(zip(instance.node_coord, instance.demand))[1:]
        ]
        for i, frm in enumerate(m.locations):
            for j, to in enumerate(m.locations):
                m.add_edge(frm, to, round(instance.edge_weight[i][j]))

        # 2 solve by pyvrp
        res = m.solve(stop=MaxRuntime(time_limit), display=True)  # one second
        # 3 transform pyvrp output to solution object
        return Solution(
            routes=[list(route) for route in res.best.routes()], cost=res.cost()
        )

    def solve_with_ortools(instance: Instance) -> Solution:
        # OR-Tools implementation would go here
        ...

    def solve_with_vroom(instance: Instance) -> Solution:
        # VROOM implementation would go here
        ...

    def solve_with_timefold(instance: Instance) -> Solution:
        # Simple timefold baseline would go here
        ...

    def solve_with_rustvrp(instance: Instance) -> Solution:
        # Simple rustvrp baseline would go here
        ...

    def solve_with_pyhygese(instance: Instance) -> Solution:
        # Simple pyhygese baseline would go here
        ...

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
