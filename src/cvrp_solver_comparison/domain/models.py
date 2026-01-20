from pydantic import BaseModel, ConfigDict
import numpy as np


class Instance(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    comment: str
    dimension: int
    edge_weight_type: str
    capacity: int
    node_coord: np.ndarray  # n x 2 matrix
    demand: np.ndarray  #  n vector
    depot: np.ndarray  # only 1 entry
    edge_weight: np.ndarray  # n x n matrix


class Solution(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    routes: list
    cost: int


def validate(solution: Solution, instance: Instance) -> bool:
    """
    Validates whether all tours of a solution are feasible regarding capacity constraint and whether the costs are correct

    :param solution: Description
    :type solution: Solution
    :param instance: Description
    :type instance: Instance
    :return: Description
    :rtype: bool
    """

    total_cost = 0

    for i, route in enumerate(solution.routes):
        distance = get_distance(route, instance)
        load = get_load(route, instance)
        total_cost += distance
        if load > instance.capacity:
            print(
                f"Tour {i} for instance {instance.name} not feasible: {load}/{instance.capacity} load."
            )
            return False
    if total_cost != solution.cost:
        print(
            f"Scores for instance {instance.name} do not match: Calculated vs in-data: {total_cost} vs {solution.cost}"
        )
        return False
    print(f"Instance and solution file for instance {instance.name} match.")
    return True


def get_distance(route: list, instance: Instance) -> float:
    depot = instance.depot[0]
    total_distance = 0
    current_stop = depot
    for stop in route:
        total_distance += round(instance.edge_weight[current_stop, stop])
        current_stop = stop
    return total_distance + round(instance.edge_weight[current_stop, depot])


def get_load(route: list, instance: Instance) -> int:
    return sum(instance.demand[stop] for stop in route)
