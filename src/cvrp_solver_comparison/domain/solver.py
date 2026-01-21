from typing import Callable
from pyvrp.stop import MaxRuntime

import pyvrp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
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
        """
        Code for solving the CVRP using pyvrp. Code heavily inspired by this documentation of the tool:
        https://pyvrp.org/examples/quick_tutorial.html

        """
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
        """
        Code for solving the CVRP using google or tools. Code heavily inspired by this documentation of the tool:
        https://developers.google.com/optimization/routing/cvrp
        """

        # create routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(instance.edge_weight), len(instance.demand), 0
        )
        # create routing model
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return round(instance.edge_weight[from_node][to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return instance.demand[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [instance.capacity for _ in instance.demand],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(time_limit)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        routes = []
        for vehicle_id in range(len(instance.demand)):
            if not routing.IsVehicleUsed(solution, vehicle_id):
                continue
            route = []
            index = routing.Start(vehicle_id)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != 0:
                    route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            routes.append(route)
        return Solution(cost=solution.ObjectiveValue(), routes=routes)

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
