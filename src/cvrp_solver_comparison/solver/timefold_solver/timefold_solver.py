from cvrp_solver_comparison.domain.models import Instance, Solution

from timefold.solver import SolverFactory
from timefold.solver.config import (
    SolverConfig,
    ScoreDirectorFactoryConfig,
    TerminationConfig,
    Duration,
)

from cvrp_solver_comparison.solver.timefold_solver.domain import (
    DistanceMatrix,
    Vehicle,
    Visit,
    VehicleRoutePlan,
)
from cvrp_solver_comparison.solver.timefold_solver.constraints import (
    define_constraints,
)


def solve_with_timefold(instance: Instance, time_limit: int) -> Solution:
    # Simple timefold baseline would go here

    solver_config = SolverConfig(
        solution_class=VehicleRoutePlan,
        entity_class_list=[Vehicle, Visit],
        score_director_factory_config=ScoreDirectorFactoryConfig(
            constraint_provider_function=define_constraints
        ),
        termination_config=TerminationConfig(spent_limit=Duration(seconds=time_limit)),
    )
    solver_factory = SolverFactory.create(solver_config)
    solver = solver_factory.build_solver()

    # transform Instance to VehicleRoutePlan
    problem = VehicleRoutePlan(
        name="test",
        vehicles=[
            Vehicle(
                f"vehicle_{i}",
                capacity=instance.capacity,
                home_location=int(instance.depot[0]),
                visits=[],
            )
            for i in range(1, len(instance.demand))
        ],
        visits=[
            Visit(
                id=i,
                name=f"visit_{i}",
                location=i,
                demand=int(instance.demand[i]),
                vehicle=None,
                previous_visit=None,
                next_visit=None,
            )
            for i in range(1, len(instance.demand))
        ],
        distance_matrix=DistanceMatrix(
            id="distance_matrix",
            matrix=[[round(entry) for entry in row] for row in instance.edge_weight],
        ),
        score=None,
        solver_status=None,
    )

    solution = solver.solve(problem=problem)
    routes = [
        [visit.id for visit in vehicle.visits]
        for vehicle in solution.vehicles
        if vehicle.visits
    ]
    score = -solution.score.soft_score
    return Solution(routes=routes, cost=score)
